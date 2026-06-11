"""
MOVIROO — scripts/dialog.py

Mode dialogue interactif  (CLI)  +  Mode API  (sans stdin).

API mode  → utiliser  DialogManager.extract_only(text)
CLI mode  → utiliser  DialogManager.run_loop()
"""

import sys
import json
import argparse
import threading
from pathlib import Path

import uvicorn


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.strict_normalization import (
    strict_postprocess,
    strict_normalize_date,
    strict_normalize_time,
    strict_normalize_location,
)
from config.knowledge import LANG_MARKERS, GOLD_EXAMPLES


# ─────────────────────────────────────────────────────────────
# TTS ENGINE
# ─────────────────────────────────────────────────────────────

LANG_VOICE_HINTS = {
    "FR": ["french", "fr_", "fr-", "français", "amelie", "thomas"],
    "EN": ["english", "en_", "en-", "david", "zira", "alex"],
    "AR": ["arabic", "ar_", "ar-", "عربي"],
    "TN": ["french", "fr_", "arabic"],
}


def _speak_in_thread(text: str, lang: str) -> None:
    def _run():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 160)
            voices = engine.getProperty("voices") or []

            hints    = LANG_VOICE_HINTS.get(lang, ["french", "english"])
            voice_id = None
            for voice in voices:
                name_low  = voice.name.lower()
                langs_low = [
                    l.lower() if isinstance(l, str) else ""
                    for l in (voice.languages or [])
                ]
                for hint in hints:
                    if hint in name_low or any(hint in l for l in langs_low):
                        voice_id = voice.id
                        break
                if voice_id:
                    break

            if not voice_id and voices:
                voice_id = voices[0].id
            if voice_id:
                engine.setProperty("voice", voice_id)

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"⚠  TTS erreur : {e}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join()


class TTSEngine:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._voices = []
        if enabled:
            self._check_available()

    def _check_available(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            self._voices = engine.getProperty("voices") or []
            engine.stop()
            print(f"🔊 TTS disponible — {len(self._voices)} voix détectées")
        except Exception as e:
            print(f"⚠  TTS non disponible : {e}")
            self.enabled = False

    def speak(self, text: str, lang: str = "FR") -> None:
        if not self.enabled:
            return
        _speak_in_thread(text, lang)

    def list_voices(self) -> None:
        for v in self._voices:
            print(f"  [{v.id}] {v.name}  langs={v.languages}")


# ─────────────────────────────────────────────────────────────
# LANGUAGE DETECTION
# ─────────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    t = text.lower()
    scores = {
        lang: sum(marker in t for marker in markers)
        for lang, markers in LANG_MARKERS.items()
    }
    best_lang  = max(scores, key=scores.get)
    best_score = scores[best_lang]

    if best_score == 0:
        if any("\u0600" <= c <= "\u06ff" for c in text):
            return "AR"
        return "FR"

    if best_lang == "AR" and scores["TN"] >= scores["AR"]:
        best_lang = "TN"

    return best_lang


# ─────────────────────────────────────────────────────────────
# QUESTIONS / CONFIRMATIONS
# ─────────────────────────────────────────────────────────────

QUESTIONS: dict[str, dict[str, str]] = {
    "destination": {
        "TN": "Wein tebghi temchi? (Destination?)",
        "FR": "Où souhaitez-vous aller ?",
        "EN": "Where would you like to go?",
        "AR": "إلى أين تريد الذهاب؟",
    },
    "date": {
        "TN": "Wa9tesh? (Quel jour?)",
        "FR": "Pour quel jour ?",
        "EN": "Which day?",
        "AR": "في أي يوم؟",
    },
    "time": {
        "TN": "Fi qaddesh el-sa3a? (À quelle heure?)",
        "FR": "À quelle heure ?",
        "EN": "At what time?",
        "AR": "في أي ساعة؟",
    },
}

CONFIRMATIONS: dict[str, str] = {
    "TN": "Mrigel! Ride men {departure} lel {destination} {date} fi {time}. Bekri bekri!",
    "FR": "Parfait ! Trajet de {departure} vers {destination} le {date} à {time}.",
    "EN": "Great! Ride from {departure} to {destination} on {date} at {time}.",
    "AR": "ممتاز! رحلة من {departure} إلى {destination} يوم {date} في {time}.",
}

MISSING_WARN: dict[str, str] = {
    "TN": "⚠  Nakso : {fields}",
    "FR": "⚠  Informations manquantes : {fields}",
    "EN": "⚠  Missing fields: {fields}",
    "AR": "⚠  معلومات ناقصة: {fields}",
}


# ─────────────────────────────────────────────────────────────
# NER WRAPPER
# ─────────────────────────────────────────────────────────────

class NERModel:
    def __init__(self, model_type: str = "bert"):
        self.model_type = model_type
        self._nlp  = None
        self._pipe = None
        self._load()

    def _load(self):
        model_path = ROOT / "models" / self.model_type
        if not model_path.exists():
            print(f"⚠  Modèle '{self.model_type}' introuvable à {model_path}")
            print("   → Mode fallback : normalisation uniquement (sans NER)")
            return

        if  self.model_type == "bert":
            from transformers import pipeline
            self._pipe = pipeline(
                "token-classification",
                model=str(model_path),
                aggregation_strategy="simple",
            )
            print(f"✅  Modèle BERT chargé : {model_path}")

        elif self.model_type == "spacy":
            import spacy
            self._nlp = spacy.load(model_path)
            print(f"✅  Modèle spaCy chargé : {model_path}") 
       

    @staticmethod
    def _clean_bert_token(word: str) -> str:
        """Strip BERT subword artifacts like '##eut' → '' (garbage)."""
        cleaned = word.strip()
        # Remove leading ## (BERT subword prefix)
        while cleaned.startswith("##"):
            cleaned = cleaned[2:]
        # If nothing meaningful remains, return empty
        return cleaned.strip()

    def predict(self, text: str) -> dict:
        raw = {"destination": None, "departure": None, "date": None, "time": None}

        if self._nlp:
            doc = self._nlp(text.lower())
            for ent in doc.ents:
                field = ent.label_.lower()
                if field in raw and raw[field] is None:
                    raw[field] = ent.text

        elif self._pipe:
            entities = self._pipe(text)
            for ent in entities:
                field = ent["entity_group"].lower()
                if field in raw and raw[field] is None:
                    cleaned = self._clean_bert_token(ent["word"])
                    if cleaned:  # skip empty / pure-subword artifacts
                        raw[field] = cleaned

        return strict_postprocess(raw, text)


# ─────────────────────────────────────────────────────────────
# DIALOG MANAGER
# ─────────────────────────────────────────────────────────────

class DialogManager:
    """
    Deux modes :
      • extract_only(text)  → API mode  — pas de stdin, retourne dict
      • run_once(text)      → CLI mode  — pose les questions manquantes
      • run_loop()          → CLI mode  — boucle interactive
    """

    SEP = "─" * 60

    def __init__(self, ner: NERModel, tts: TTSEngine):
        self.ner = ner
        self.tts = tts

    # ── API MODE ─────────────────────────────────────────────

    def extract_only(self, text: str) -> dict:
        """
        Mode API : extrait les entités sans poser de questions.
        Utilisé directement par FastAPI après transcription Whisper.

        Retourne :
        {
          "destination":    str | None,
          "departure":      str | None,
          "date":           str | None,
          "time":           str | None,
          "missing_fields": list[str],
          "lang":           str,
          "confirmation":   str | None,
        }
        """
        lang   = detect_language(text)
        result = self.ner.predict(text)

        # Calcul des champs manquants
        result["missing_fields"] = [
            f for f in ["destination", "date", "time"] if not result.get(f)
        ]
        result["lang"] = lang

        # Confirmation seulement si tout est présent
        if not result["missing_fields"]:
            result["confirmation"] = self._build_confirmation(result, lang)
        else:
            result["confirmation"] = None

        return result

    def _build_confirmation(self, result: dict, lang: str) -> str:
        tpl = CONFIRMATIONS.get(lang, CONFIRMATIONS["FR"])
        return tpl.format(
            departure=result.get("departure") or "position actuelle",
            destination=result.get("destination") or "?",
            date=result.get("date") or "?",
            time=result.get("time") or "?",
        )

    # ── CLI MODE ─────────────────────────────────────────────

    def _ask(self, field: str, lang: str) -> str:
        question = QUESTIONS[field][lang]
        print(f"\n❓  {question}")
        self.tts.speak(question, lang)
        return input("   > ").strip()

    def _confirm(self, result: dict, lang: str) -> None:
        msg = self._build_confirmation(result, lang)
        print(f"\n✅  {msg}")
        self.tts.speak(msg, lang)

    def _print_result(self, result: dict) -> None:
        print(f"\n{'─'*40}")
        print(f"  🗺  Destination : {result.get('destination') or '—'}")
        print(f"  🚩  Départ      : {result.get('departure')  or '—'}")
        print(f"  📅  Date        : {result.get('date')       or '—'}")
        print(f"  🕐  Heure       : {result.get('time')       or '—'}")
        if result.get("missing_fields"):
            print(f"  ⚠  Manquants   : {', '.join(result['missing_fields'])}")
        print(f"{'─'*40}")

    def run_once(self, user_input: str) -> dict:
        lang   = detect_language(user_input)
        result = self.ner.predict(user_input)
        self._print_result(result)

        for field in list(result.get("missing_fields", [])):
            answer = self._ask(field, lang)
            if answer:
                # When answering a specific field, always use strict normalizer directly
                # BERT might misclassify (e.g., "15" as time instead of date)
                if field == "date":
                    result["date"] = strict_normalize_date(answer)
                elif field == "time":
                    result["time"] = strict_normalize_time(answer)
                elif field == "destination":
                    result["destination"] = strict_normalize_location(answer)

        result["missing_fields"] = [
            f for f in ["destination", "date", "time"] if not result.get(f)
        ]

        if not result.get("missing_fields"):
            self._confirm(result, lang)
        else:
            warn = MISSING_WARN.get(lang, MISSING_WARN["FR"])
            msg  = warn.format(fields=", ".join(result["missing_fields"]))
            print(f"\n{msg}")
            self.tts.speak(msg, lang)

        return result

    def run_loop(self) -> None:
        print(f"\n{self.SEP}")
        print("MOVIROO — Mode Dialogue")
        print("   Saisissez votre demande (q pour quitter)")
        print(f"{self.SEP}\n")

        while True:
            try:
                user_input = input("📝 > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋  Au revoir !")
                break

            if not user_input:
                continue
            if user_input.lower() in ("q", "quit", "exit", "خروج"):
                print("👋  Au revoir !")
                break

            result = self.run_once(user_input)
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
            print(f"\n{self.SEP}")


# ─────────────────────────────────────────────────────────────
# MAIN  (CLI uniquement)
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MOVIROO — Mode dialogue interactif")
    parser.add_argument("--model",  default="spacy", choices=["spacy", "bert"])
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--voices", action="store_true")
    args = parser.parse_args()

    tts = TTSEngine(enabled=not args.no_tts)

    if args.voices:
        tts.list_voices()
        return

    ner    = NERModel(model_type=args.model)
    dialog = DialogManager(ner=ner, tts=tts) 
    dialog.run_loop()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005 , reload=True)
    # main()