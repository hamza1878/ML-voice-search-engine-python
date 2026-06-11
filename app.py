"""
MOVIROO — api/app.py

REST API Flask pour le pipeline dialogue vocal.
Endpoints:
    POST /dialog/start   → texte ou audio → NER → {result, missing_fields, next_question}
    POST /dialog/answer  → réponse à une question manquante → même structure
    GET  /dialog/status/<session_id> → état courant de la session

Sessions stockées en mémoire (dict). Pour production → Redis.

Usage:
    pip install flask flask-cors
    python api/app.py
"""

import sys
import uuid
import json
import time
import tempfile
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import uvicorn

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.normalization import postprocess, normalize_date, normalize_time, normalize_location
from scripts.dialog import detect_language, QUESTIONS, CONFIRMATIONS, MISSING_WARN

app = Flask(__name__)
CORS(app)  # autorise toutes les origines (Flutter en dev)

# ── Session store (in-memory) ─────────────────────────────────────────────────
# structure : { session_id: { "result": {...}, "lang": "FR", "pending": [...], "done": bool } }
SESSIONS: dict[str, dict] = {}

SESSION_TTL = 600  # 10 minutes d'inactivité → nettoyage
_session_ts: dict[str, float] = {}


def _touch(sid: str) -> None:
    _session_ts[sid] = time.time()


def _cleanup_old_sessions() -> None:
    now = time.time()
    dead = [k for k, t in _session_ts.items() if now - t > SESSION_TTL]
    for k in dead:
        SESSIONS.pop(k, None)
        _session_ts.pop(k, None)


# ── NER loader (lazy, singleton) ─────────────────────────────────────────────
_ner_instance = None


def get_ner(model_type: str = "spacy"):
    global _ner_instance
    if _ner_instance is None:
        from scripts.dialog import NERModel
        _ner_instance = NERModel(model_type=model_type)
    return _ner_instance


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_response(session_id: str) -> dict:
    """Construit la réponse JSON standard depuis l'état de session."""
    session = SESSIONS[session_id]
    result  = session["result"]
    lang    = session["lang"]
    pending = session.get("pending", [])

    response = {
        "session_id":     session_id,
        "lang":           lang,
        "destination":    result.get("destination"),
        "departure":      result.get("departure"),
        "date":           result.get("date"),
        "time":           result.get("time"),
        "missing_fields": result.get("missing_fields", []),
        "done":           session.get("done", False),
        "confirmation":   None,
        "next_question":  None,
        "next_field":     None,
    }

    if session.get("done"):
        tpl = CONFIRMATIONS.get(lang, CONFIRMATIONS["FR"])
        response["confirmation"] = tpl.format(
            departure=result.get("departure") or "position actuelle",
            destination=result.get("destination") or "?",
            date=result.get("date") or "?",
            time=result.get("time") or "?",
        )
    elif pending:
        next_field = pending[0]
        response["next_field"]    = next_field
        response["next_question"] = QUESTIONS.get(next_field, {}).get(lang, "?")

    return response


def _process_text(text: str, session: dict) -> None:
    """Lance le NER sur `text` et met à jour la session."""
    ner    = get_ner()
    result = ner.predict(text)
    lang   = detect_language(text)

    session["lang"]   = lang
    session["result"] = result
    session["pending"] = list(result.get("missing_fields", []))
    session["done"]    = len(session["pending"]) == 0


def _fill_field(field: str, answer: str, session: dict) -> None:
    """Remplit un champ manquant depuis la réponse utilisateur."""
    ner    = get_ner()
    result = session["result"]
    lang   = session["lang"]

    # Essai NER sur la réponse courte
    partial = ner.predict(answer)
    if partial.get(field):
        result[field] = partial[field]
    else:
        # Fallback normalisation directe
        if field == "date":
            result["date"] = normalize_date(answer) or answer
        elif field == "time":
            result["time"] = normalize_time(answer) or answer
        elif field in ("destination", "departure"):
            result[field] = normalize_location(answer) or answer

    # Recalcul des manquants
    missing = [f for f in ["destination", "date", "time"] if not result.get(f)]
    result["missing_fields"] = missing

    # Retire le champ de la file d'attente
    pending = session.get("pending", [])
    if field in pending:
        pending.remove(field)
    session["pending"] = missing  # resync avec missing réel
    session["done"]    = len(missing) == 0


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "spacy"})


@app.route("/dialog/start", methods=["POST"])
def dialog_start():
    """
    Démarre une nouvelle session de dialogue.

    Body JSON  : { "text": "nheb nemchi hammamet ghodwa 18h" }
    Body multi : fichier audio dans le champ 'audio' (mp3/wav/m4a)

    Returns: réponse standard avec session_id + next_question si champs manquants.
    """
    _cleanup_old_sessions()

    session_id = str(uuid.uuid4())
    session: dict = {"result": {}, "lang": "FR", "pending": [], "done": False}
    SESSIONS[session_id] = session
    _touch(session_id)

    # ── Mode texte ────────────────────────────────────────────────────────────
    if request.is_json:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Champ 'text' manquant"}), 400
        _process_text(text, session)

    # ── Mode audio → AssemblyAI STT ───────────────────────────────────────────
    elif "audio" in request.files:
        audio_file = request.files["audio"]
        suffix = Path(audio_file.filename or "audio.mp3").suffix or ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name
        try:
            from scripts.moviroo_voice_pipeline import speech_to_text # type: ignore
            text = speech_to_text(tmp_path)
            _process_text(text, session)
            session["result"]["transcript"] = text
        finally:
            os.unlink(tmp_path)

    else:
        return jsonify({"error": "Fournir 'text' (JSON) ou fichier 'audio'"}), 400

    return jsonify(_build_response(session_id)), 200


@app.route("/dialog/answer", methods=["POST"])
def dialog_answer():
    """
    Envoie la réponse à la question posée par l'API.

    Body JSON : { "session_id": "...", "field": "date", "answer": "demain" }

    Returns: réponse standard mise à jour.
    """
    data       = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()
    field      = data.get("field", "").strip()
    answer     = data.get("answer", "").strip()

    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "session_id invalide ou expiré"}), 404
    if not field:
        return jsonify({"error": "Champ 'field' manquant"}), 400
    if not answer:
        return jsonify({"error": "Champ 'answer' manquant"}), 400

    session = SESSIONS[session_id]
    _touch(session_id)
    _fill_field(field, answer, session)

    return jsonify(_build_response(session_id)), 200


@app.route("/dialog/status/<session_id>", methods=["GET"])
def dialog_status(session_id: str):
    """Retourne l'état courant d'une session."""
    if session_id not in SESSIONS:
        return jsonify({"error": "session_id invalide ou expiré"}), 404
    _touch(session_id)
    return jsonify(_build_response(session_id)), 200


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=False)
