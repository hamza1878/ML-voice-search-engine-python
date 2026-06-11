"""
MOVIROO — backend/services/dialog_service.py

Multi-turn conversation manager.

Each session stores:
  - data  : collected booking fields
  - lang  : detected language
  - turns : number of exchanges

State is held in memory (dict).
For production, swap _sessions with Redis / a DB.
"""

import re
import threading
from copy import deepcopy
from services.nlp_service import NLPService


# ─────────────────────────────────────────────────────────────
# LANGUAGE DETECTION
# ─────────────────────────────────────────────────────────────

LANG_MARKERS = {
    "TN": ["nheb", "nemchi", "ghodwa", "tawwa", "wein", "tebghi", "mrigel",
           "lel", "wa9tesh", "sa3a", "bekri", "min", "3and"],
    "FR": ["je veux", "aller", "demain", "matin", "soir", "depuis", "vers",
           "vendredi", "samedi", "réserver", "partir", "pour"],
    "EN": ["i want", "take me", "i need", "go to", "from", "to the",
           "tomorrow", "tonight", "monday", "friday", "cab", "ride"],
    "AR": ["إلى", "من", "غداً", "غدا", "مساء", "صباح",
           "أريد", "احتاج", "المطار"],
}


def detect_language(text: str) -> str:
    t = text.lower()
    scores = {
        lang: sum(1 for m in markers if m in t)
        for lang, markers in LANG_MARKERS.items()
    }
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        # Arabic unicode range fallback
        if any("\u0600" <= c <= "\u06ff" for c in text):
            return "AR"
        return "FR"
    if best == "AR" and scores["TN"] >= scores["AR"]:
        return "TN"
    return best


# ─────────────────────────────────────────────────────────────
# QUESTION TEMPLATES
# ─────────────────────────────────────────────────────────────

QUESTIONS: dict[str, dict[str, str]] = {
    "destination": {
        "TN": "Wein tebghi temchi? (Destination?)",
        "FR": "Où souhaitez-vous aller ?",
        "EN": "Where would you like to go?",
        "AR": "إلى أين تريد الذهاب؟",
    },
    "date": {
        "TN": "Wa9tesh? Quel jour?",
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
    "departure": {
        "TN": "Min wein tetla3? (Point de départ?)",
        "FR": "D'où partez-vous ?",
        "EN": "Where are you departing from?",
        "AR": "من أين ستنطلق؟",
    },
}

CONFIRMATIONS: dict[str, str] = {
    "TN": "Mrigel! Ride men {departure} lel {destination} {date} fi {time}. Confirmed!",
    "FR": "Parfait ! Trajet de {departure} vers {destination} le {date} à {time}.",
    "EN": "Great! Ride from {departure} to {destination} on {date} at {time}.",
    "AR": "ممتاز! رحلة من {departure} إلى {destination} يوم {date} في {time}.",
}

# Required fields (departure is optional — defaults to "current location")
REQUIRED_FIELDS = ["destination", "date", "time"]
ALL_FIELDS      = ["destination", "departure", "date", "time"]


# ─────────────────────────────────────────────────────────────
# SESSION MODEL
# ─────────────────────────────────────────────────────────────

def _empty_session() -> dict:
    return {
        "data": {f: None for f in ALL_FIELDS},
        "lang": "FR",
        "turns": 0,
        "asked": [],         # fields already asked once
    }


# ─────────────────────────────────────────────────────────────
# DIALOG SERVICE
# ─────────────────────────────────────────────────────────────

class DialogService:
    """
    Thread-safe multi-turn dialog manager.
    Each call to process_text() advances the conversation by one turn.
    """

    def __init__(self):
        self.nlp_service = NLPService()
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()

    # ── Session helpers ───────────────────────────────────────

    def _get_or_create(self, session_id: str) -> dict:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = _empty_session()
            return self._sessions[session_id]

    def clear_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    # ── Merge helpers ─────────────────────────────────────────

    @staticmethod
    def _merge(existing: dict, new: dict) -> dict:
        """Only overwrite None values — never discard already-known data."""
        merged = deepcopy(existing)
        for field in ALL_FIELDS:
            if merged[field] is None and new.get(field):
                merged[field] = new[field]
        return merged

    # ── Next question ─────────────────────────────────────────

    @staticmethod
    def _next_question(missing: list[str], asked: list[str], lang: str) -> str | None:
        """Return the first unanswered REQUIRED question not yet asked."""
        for field in REQUIRED_FIELDS:
            if field in missing and field not in asked:
                return QUESTIONS[field][lang]
        return None

    # ── Confirmation message ──────────────────────────────────

    @staticmethod
    def _build_confirmation(data: dict, lang: str) -> str:
        tpl = CONFIRMATIONS.get(lang, CONFIRMATIONS["FR"])
        return tpl.format(
            departure=data.get("departure") or "votre position",
            destination=data.get("destination") or "?",
            date=data.get("date") or "?",
            time=data.get("time") or "?",
        )

    # ── Main entry point ──────────────────────────────────────

    def process_text(self, session_id: str, text: str) -> dict:
        """
        Process one user turn.

        Returns:
            {
                response:       str,      # bot reply
                data:           dict,     # current booking data
                complete:       bool,
                missing_fields: list[str],
            }
        """
        session = self._get_or_create(session_id)

        # 1. Detect language (update if first turn or re-detected)
        detected_lang = detect_language(text)
        if session["turns"] == 0 or detected_lang != "FR":
            session["lang"] = detected_lang
        lang = session["lang"]

        # 2. Run NLP
        nlp_result = self.nlp_service.predict(text)

        # 3. Merge into session data
        session["data"] = self._merge(session["data"], nlp_result)
        session["turns"] += 1

        # 4. Compute missing REQUIRED fields
        missing = [f for f in REQUIRED_FIELDS if not session["data"].get(f)]

        # 5. Build response
        if not missing:
            # ── All required fields collected ─────────────────
            response = self._build_confirmation(session["data"], lang)
            complete = True
        else:
            # ── Ask the next un-asked question ────────────────
            question = self._next_question(missing, session["asked"], lang)
            if question:
                # Mark field as asked
                for f in REQUIRED_FIELDS:
                    if f in missing and f not in session["asked"]:
                        session["asked"].append(f)
                        break
                response = question
            else:
                # All required fields have been asked, still missing → accept gracefully
                response = self._build_confirmation(session["data"], lang)
                complete = True
            complete = not missing

        return {
            "response":       response,
            "data":           deepcopy(session["data"]),
            "complete":       complete,
            "missing_fields": missing,
        }