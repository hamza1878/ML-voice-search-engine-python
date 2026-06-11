"""
MOVIROO — backend/main.py  (v7.0 — fix merge + missing_fields)
"""

import os
import re
import sys
import tempfile
import logging
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.hybrid import hybrid_predict, _load_spacy, _load_bert
from config.strict_normalization import strict_postprocess, strip_fillers

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="MOVIROO API", version="7.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Modèles (chargés une seule fois) ─────────────────────────
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "tiny")  # tiny, base, small, medium, large
whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
logger.info("Whisper ✓  (model=%s)", WHISPER_MODEL_SIZE)

_nlp  = _load_spacy()
logger.info("spaCy ✓")

_pipe = _load_bert()
logger.info("BERT ✓")

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".mp4"}

_LANG_MAP = {
    "arabic":   "ar",
    "french":   "fr",
    "english":  "en",
    "tunisian": "tn",
}

BOOKING_KEYWORDS = {
    "fr": ["aller", "départ", "destination", "réserver", "réservation",
           "amène", "conduis", "vers", "depuis", "de ", "à "],
    "ar": ["اذهب", "أريد", "وصول", "مغادرة", "إلى", "من"],
    "en": ["ride", "cab", "go to", "take me", "from", "to", "book"],
    "tn": ["nemchi", "nroh", "wين", "men", "lel", "nheb", "bech", "roh"],
}

QUESTIONS = {
    "destination": {
        "fr": "Où souhaitez-vous aller ?",
        "ar": "إلى أين تريد الذهاب ؟",
        "en": "Where would you like to go?",
        "tn": "Wين تحب تمشي ؟",
    },
    "date": {
        "fr": "Quelle date souhaitez-vous ?",
        "ar": "ما هو تاريخ الرحلة ؟",
        "en": "What date would you like?",
        "tn": "Enti فاش تحب تمشي ؟",
    },
    "time": {
        "fr": "À quelle heure ?",
        "ar": "في أي وقت ؟",
        "en": "At what time?",
        "tn": "Wقتاش بالضبط ؟",
    },
}

CONFIRMATIONS = {
    "fr": "Trajet de {departure} vers {destination} le {date} à {time}. Confirmé !",
    "ar": "رحلة من {departure} إلى {destination} يوم {date} في {time}. مؤكد !",
    "en": "Ride from {departure} to {destination} on {date} at {time}. Confirmed!",
    "tn": "Ride من {departure} لـ {destination} يوم {date} في {time}. Mrigel !",
}

DEFAULT_DEPARTURE = "current_location"

# ── Champs OBLIGATOIRES pour la confirmation ──────────────────
# departure est OPTIONNEL : s'il manque on met current_location
REQUIRED_FIELDS = ["destination", "date", "time"]


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def normalize_lang(whisper_lang: str) -> str:
    if not whisper_lang:
        return "fr"
    key = whisper_lang.lower().strip()
    if len(key) == 2:
        return key
    return _LANG_MAP.get(key, key[:2])


def detect_intent(text: str, lang: str) -> str:
    text_lower = text.lower()
    keywords = BOOKING_KEYWORDS.get(lang, []) + BOOKING_KEYWORDS.get("en", [])
    for kw in keywords:
        if kw in text_lower:
            return "booking"
    return "search"


def extract_entities(text: str) -> dict:
    """NER hybride + strict normalization."""
    # hybrid_predict already calls strict_postprocess internally,
    # so we must NOT call it again (it would re-normalize "current_location"
    # through strict_normalize_location which rejects it as a location name).
    result = hybrid_predict(text, nlp=_nlp, pipe=_pipe)
    # departure absent → current_location par défaut
    if not result.get("departure"):
        result["departure"] = DEFAULT_DEPARTURE
    return result


def compute_missing(entities: dict) -> list[str]:
    """
    FIX v7 : departure n'est JAMAIS dans missing_fields.
    On ne demande que destination, date, time.
    """
    return [f for f in REQUIRED_FIELDS if not entities.get(f)]


_DEPARTURE_DISPLAY = {
    "fr": "votre position actuelle",
    "ar": "موقعك الحالي",
    "en": "your current location",
    "tn": "win inti tawa",
}


def build_confirmation(entities: dict, lang: str) -> Optional[str]:
    missing = compute_missing(entities)
    if missing:
        return None
    tpl = CONFIRMATIONS.get(lang, CONFIRMATIONS["fr"])
    dep = entities.get("departure") or DEFAULT_DEPARTURE
    if dep == DEFAULT_DEPARTURE:
        dep = _DEPARTURE_DISPLAY.get(lang, _DEPARTURE_DISPLAY["en"])
    return tpl.format(
        departure=dep,
        destination=entities.get("destination") or "?",
        date=entities.get("date") or "?",
        time=entities.get("time") or "?",
    )


def build_next_question(missing: list, lang: str) -> Optional[dict]:
    if not missing:
        return None
    field = missing[0]
    lang_questions = QUESTIONS.get(field, {})
    question = lang_questions.get(lang) or lang_questions.get("fr", "?")
    return {"field": field, "question": question}


def clean_time(raw: str | None) -> str | None:
    """
    FIX v7 : nettoie '8h.' → '08:00', '8 PM' → '20:00', '8 AM' → '08:00'.
    """
    import re
    if not raw:
        return None
    text = raw.strip().rstrip(".,!?؟ ")

    # AM / PM
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([AaPp][Mm])", text)
    if m:
        h  = int(m.group(1))
        mn = int(m.group(2)) if m.group(2) else 0
        if m.group(3).upper() == "AM":
            h = 0 if h == 12 else h
        else:
            h = h if h == 12 else h + 12
        return f"{h:02d}:{mn:02d}"

    # 18h / 8h30
    m = re.search(r"(\d{1,2})h(\d{0,2})", text)
    if m:
        h  = int(m.group(1))
        mn = int(m.group(2)) if m.group(2) else 0
        return f"{h:02d}:{mn:02d}"

    # 14:00
    m = re.search(r"(\d{1,2}):(\d{2})", text)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    # Bare number (1-24) → treat as hour ONLY if not part of a date pattern
    # Skip numbers followed by month names (e.g., "15 juin")
    m = re.search(r"\b(\d{1,2})\b", text)
    if m:
        num = m.group(0)
        # Check if this number is part of a date expression (e.g., "15 juin", "1er juillet")
        date_month_check = re.search(
            r"\b\d{1,2}(?:\s*er)?\s+(?:"
            + "janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|"
            + "septembre|octobre|novembre|décembre|decembre|"
            + "جانفي|يناير|فيفري|فبراير|مارس|أفريل|افريل|إبريل|ابريل|"
            + "ماي|مايو|جوان|يونيو|جويلية|يوليو|أوت|اوت|غشت|أغسطس|اغسطس|"
            + "سبتمبر|septembre|أكتوبر|اكتوبر|نوفمبر|ديسمبر|ديسانبر"
            + r")\b",
            text.lower(),
        )
        if not date_month_check:
            h = int(m.group(1))
            if 0 <= h <= 24:
                return f"{h:02d}:00"

    # Sémantique (FR + EN + AR + TN)
    _SEMANTIC_TIME = {
        # EN
        "morning": "08:00", "noon": "12:00", "afternoon": "14:00",
        "evening": "19:00", "night": "22:00", "midnight": "00:00",
        # FR
        "matin": "08:00", "midi": "12:00", "après-midi": "14:00",
        "apres-midi": "14:00", "apres midi": "14:00",
        "soir": "19:00", "soirée": "19:00", "soiree": "19:00",
        "nuit": "22:00", "minuit": "00:00",
        # AR
        "صباح": "08:00", "صباحا": "08:00", "ظهر": "12:00",
        "مساء": "19:00", "ليل": "22:00", "منتصف الليل": "00:00",
        # TN
        "sba7": "08:00", "dhor": "12:00", "3chiya": "19:00",
        "lil": "22:00", "nos ellil": "00:00",
    }
    return _SEMANTIC_TIME.get(text.lower(), text)   # fallback : renvoie le texte brut plutôt que None


async def _transcribe_file(
    file: UploadFile,
    language_hint: str | None = None,
) -> tuple[str, str]:
    suffix = Path(file.filename or "audio.wav").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, f"Format non supporté : {suffix}")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(400, "Fichier audio vide")
    if len(audio_bytes) > 100 * 1024 * 1024:
        raise HTTPException(413, "Fichier trop grand (max 100 MB)")

    # Normalize hint to 2-letter code Whisper expects
    whisper_lang = None
    if language_hint:
        code = language_hint[:2].lower()
        if code == "tn":
            whisper_lang = "ar"       # Tunisian → Arabic for Whisper
        elif code in {"fr", "en", "ar"}:
            whisper_lang = code

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        segments, info = whisper_model.transcribe(
            tmp_path,
            language=whisper_lang,
            task="transcribe",
            beam_size=5,
            temperature=0,
            vad_filter=False,
            condition_on_previous_text=False,
        )
        raw_text = "".join(seg.text for seg in segments).strip()
        lang = normalize_lang(info.language)
        return raw_text, lang
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ─────────────────────────────────────────────────────────────
# GET /health
# ─────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "whisper": WHISPER_MODEL_SIZE, "ner": "hybrid (BERT + spaCy)"}


# ─────────────────────────────────────────────────────────────
# POST /transcribe
# ─────────────────────────────────────────────────────────────
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        raw_text, lang = await _transcribe_file(file)
        logger.info("Whisper: lang=%s | '%s'", lang, raw_text[:80])

        intent = detect_intent(raw_text, lang)
        logger.info("Intent: %s", intent)

        response: dict = {"text": raw_text, "language": lang, "intent": intent}

        if intent == "search":
            response["search_query"] = raw_text.strip()
        else:
            entities          = extract_entities(raw_text)
            entities["time"]  = clean_time(entities.get("time"))   # FIX: normalise time
            missing           = compute_missing(entities)

            response.update({
                "destination":    entities.get("destination"),
                "departure":      entities.get("departure"),
                "date":           entities.get("date"),
                "time":           entities.get("time"),
                "missing_fields": missing,
                "next_question":  build_next_question(missing, lang),
                "confirmation":   build_confirmation(entities, lang),
            })

        logger.info("Response: %s", response)
        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Pipeline error")
        raise HTTPException(500, str(exc))


# ─────────────────────────────────────────────────────────────
# POST /answer  — FIX v7 : fusion correcte contexte + nouvelle valeur
# ─────────────────────────────────────────────────────────────
@app.post("/answer")
async def answer_missing_field(
    file:        UploadFile    = File(...),
    field:       str           = Query("destination"),
    language:    str           = Query("fr"),
    destination: Optional[str] = Query(None),
    departure:   Optional[str] = Query(None),
    date:        Optional[str] = Query(None),
    time:        Optional[str] = Query(None),
):
    try:
        raw_text, detected_lang = await _transcribe_file(file, language_hint=language)
        logger.info("Answer field=%s lang=%s text='%s'", field, language, raw_text)

        lang = language[:2].lower() if language else detected_lang

        # NER sur la réponse
        new_entities = extract_entities(raw_text)

        # Valeur extraite pour le champ attendu
        # Priorité : NER du nouveau texte → texte brut en fallback
        new_value = new_entities.get(field) or raw_text.strip()

        # For time field: try clean_time on raw text as extra fallback
        if field == "time" and not new_entities.get("time"):
            cleaned_time = clean_time(raw_text.strip())
            if cleaned_time and re.search(r"\d", cleaned_time or ""):
                new_value = cleaned_time

        # For date field: try natural language parsing directly (e.g., "15 juin")
        if field == "date" and not new_entities.get("date"):
            from config.strict_normalization import strict_normalize_date
            parsed_date = strict_normalize_date(raw_text.strip())
            if parsed_date:
                new_value = parsed_date

        # FIX v7 : MERGE correct
        # Règle : nouvelle valeur du champ répond > contexte existant
        #         pour tous les AUTRES champs : contexte existant > nouvelle extraction
        # FIX v8 : If departure is just the default "current_location", prefer
        #          newly extracted departure so "Tunis vers Hammamet" works.
        ctx_departure = departure
        if ctx_departure == DEFAULT_DEPARTURE and new_entities.get("departure") \
                and new_entities["departure"] != DEFAULT_DEPARTURE:
            ctx_departure = None  # let new extraction take over

        merged = {
            "destination": destination or new_entities.get("destination"),
            "departure":   ctx_departure or new_entities.get("departure") or DEFAULT_DEPARTURE,
            "date":        date        or new_entities.get("date"),
            "time":        time        or new_entities.get("time"),
        }
        # Le champ qui vient d'être répondu : valeur fraîche obligatoire
        merged[field] = new_value

        # Strict normalization on merged values
        merged = strict_postprocess(merged, raw_text)
        # FIX: clean_time on the final time value (handles "8h." → "08:00")
        merged["time"] = clean_time(merged.get("time"))
        if not merged.get("departure"):
            merged["departure"] = DEFAULT_DEPARTURE

        missing = compute_missing(merged)

        logger.info("Merged: %s | missing: %s", merged, missing)

        return JSONResponse(content={
            "text":           raw_text,
            "language":       lang,
            "intent":         "booking",
            "destination":    merged["destination"],
            "departure":      merged["departure"],
            "date":           merged["date"],
            "time":           merged["time"],
            "missing_fields": missing,
            "next_question":  build_next_question(missing, lang),
            "confirmation":   build_confirmation(merged, lang),
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Answer error")
        raise HTTPException(500, str(exc))


# ─────────────────────────────────────────────────────────────
# POST /dialog  — debug texte direct
# ─────────────────────────────────────────────────────────────
class DialogPayload(BaseModel):
    text:     str
    language: str = "fr"


@app.post("/dialog")
async def dialog_text(payload: DialogPayload):
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "Le champ 'text' est requis")

    lang   = payload.language[:2].lower()
    intent = detect_intent(text, lang)

    if intent == "search":
        return JSONResponse({
            "text": text, "language": lang,
            "intent": "search", "search_query": text,
        })

    entities         = extract_entities(text)
    entities["time"] = clean_time(entities.get("time"))
    missing          = compute_missing(entities)

    return JSONResponse({
        "text":           text,
        "language":       lang,
        "intent":         "booking",
        "destination":    entities.get("destination"),
        "departure":      entities.get("departure"),
        "date":           entities.get("date"),
        "time":           entities.get("time"),
        "missing_fields": missing,
        "next_question":  build_next_question(missing, lang),
        "confirmation":   build_confirmation(entities, lang),
    })


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=False)