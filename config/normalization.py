"""
MOVIROO — config/normalization.py

Fonctions de normalisation pour date, heure, lieu.
Toutes les maps de données viennent de config/knowledge.py.
"""

import re
from datetime import date, timedelta

from config.knowledge import (
    LOCATION_ALIASES,
    TIME_TRIGGER_MAP,
    DATE_TRIGGER_MAP,
)

# ─────────────────────────────────────────────────────────────
# DATE MAP — triggers + variantes dialectales supplémentaires
# ─────────────────────────────────────────────────────────────

DATE_MAP: dict[str, str] = {
    **DATE_TRIGGER_MAP,
    # ── variantes TN non couvertes par les triggers ───────────
    "lioum":               "today",
    "tawwali":             "now",
    "ghodoa":              "tomorrow",
    "el-jemaa el-jaya":   "next_friday",
    "jemaa":               "friday",
    "khamis":              "thursday",
    "ahad":                "sunday",
    "itnin":               "monday",
    "talata":              "tuesday",
    "arba3":               "wednesday",
    "sebt":                "saturday",
    "el-sebt":             "saturday",
    "el-lil":              "tonight",
    # ── variantes FR ─────────────────────────────────────────
    "aujourdhui":          "today",
    "apres-demain":        "day_after_tomorrow",
    "apres demain":        "day_after_tomorrow",
    "ce matin":            "today",
    "lundi prochain":      "next_monday",
    "vendredi prochain":   "next_friday",
    "dimanche prochain":   "next_sunday",
    # ── variantes EN ─────────────────────────────────────────
    "next monday":         "next_monday",
    "next tuesday":        "next_tuesday",
    "next wednesday":      "next_wednesday",
    "next thursday":       "next_thursday",
    "next friday":         "next_friday",
    "next saturday":       "next_saturday",
    "next sunday":         "next_sunday",
    "this friday":         "friday",
    "this saturday":       "saturday",
    "this sunday":         "sunday",
    "this tuesday":        "tuesday",
    "day after tomorrow":  "day_after_tomorrow",
    # ── variantes AR ─────────────────────────────────────────
    "غداً":                "tomorrow",
    "مساء الجمعة":         "friday",
    "الاثنين القادم":      "next_monday",
    "الجمعة القادمة":      "next_friday",
}

# ─────────────────────────────────────────────────────────────
# TIME MAP — triggers + alias supplémentaires
# ─────────────────────────────────────────────────────────────

TIME_MAP: dict[str, str] = {
    **TIME_TRIGGER_MAP,
    # ── variantes TN ─────────────────────────────────────────
    "fel sbeh":        "morning",
    "fel 3achiya":     "evening",
    "fel dhuhr":       "noon",
    "nouss el-lil":    "midnight",
    "el-lil":          "night",
    # ── variantes FR ─────────────────────────────────────────
    "apres-midi":      "afternoon",
    "après-midi":      "afternoon",
    "apres midi":      "afternoon",
    "minuit":          "midnight",
    # ── variantes AR ─────────────────────────────────────────
    "مساءً":           "evening",
    "منتصف الليل":     "midnight",
}

# ─────────────────────────────────────────────────────────────
# LOCATION MAP — directement depuis knowledge.LOCATION_ALIASES
# ─────────────────────────────────────────────────────────────

LOCATION_MAP: dict[str, str] = LOCATION_ALIASES

# ─────────────────────────────────────────────────────────────
# DELTA & DAY TABLES
# ─────────────────────────────────────────────────────────────

DATE_DELTA: dict[str, int] = {
    "today": 0, "now": 0, "tomorrow": 1,
    "day_after_tomorrow": 2, "tonight": 0,
}

DAY_NAMES: dict[str, int] = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

NEXT_DAY_NAMES: dict[str, int] = {
    f"next_{k}": v for k, v in DAY_NAMES.items()
}

# ─────────────────────────────────────────────────────────────
# FALLBACK REGEX
# ─────────────────────────────────────────────────────────────

FALLBACK_RULES = [
    (re.compile(r"\b(\d{1,2}h\d{0,2}|\d{1,2}:\d{2}|\d{1,2}(?:am|pm))\b", re.I), "time"),
    (re.compile(r"\ble\s*\d{1,2}\b|\b\d{1,2}[/\-]\d{1,2}\b",              re.I), "date"),
]

# ─────────────────────────────────────────────────────────────
# NORMALIZE FUNCTIONS
# ─────────────────────────────────────────────────────────────

def normalize_date(raw: str | None) -> str | None:
    """
    Convertit un token date brut en ISO (YYYY-MM-DD) ou label sémantique.

    Priorité :
      1. DATE_MAP  → keyword → canonical label
      2. DATE_DELTA → offset depuis aujourd'hui → ISO
      3. DAY_NAMES  → prochain jour de la semaine → ISO
      4. NEXT_DAY_NAMES → semaine suivante → ISO
      5. Regex JJ/MM[-YYYY] → ISO
      6. Retour brut
    """
    if not raw:
        return None
    key    = raw.lower().strip()
    mapped = DATE_MAP.get(key, key)
    today  = date.today()

    if mapped in DATE_DELTA:
        return (today + timedelta(days=DATE_DELTA[mapped])).isoformat()

    if mapped == "tonight":
        return today.isoformat()

    if mapped in DAY_NAMES:
        ahead = (DAY_NAMES[mapped] - today.weekday()) % 7
        if ahead == 0:
            ahead = 7
        return (today + timedelta(days=ahead)).isoformat()

    if mapped in NEXT_DAY_NAMES:
        target = NEXT_DAY_NAMES[mapped]
        ahead  = (target - today.weekday()) % 7
        if ahead == 0:
            ahead = 7
        return (today + timedelta(days=ahead)).isoformat()

    m = re.match(r"(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{4}))?$", key)
    if m:
        try:
            d = date(
                int(m.group(3) or today.year),
                int(m.group(2)),
                int(m.group(1)),
            )
            return d.isoformat()
        except ValueError:
            pass

    return mapped or None


def normalize_time(raw: str | None) -> str | None:
    """
    Convertit un token heure brut en HH:MM ou label sémantique.

    Priorité :
      1. TIME_MAP  → keyword → semantic label
      2. Regex 18h / 8h30 → HH:MM
      3. Regex 14:00      → HH:MM
      4. Regex 9am / 10pm → HH:MM
      5. Retour brut
    """
    if not raw:
        return None
    key = raw.lower().strip()

    if key in TIME_MAP:
        return TIME_MAP[key]

    m = re.match(r"(\d{1,2})h(\d{0,2})$", key)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2) or 0):02d}"

    m = re.match(r"(\d{1,2}):(\d{2})$", key)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    m = re.match(r"(\d{1,2})(am|pm)$", key)
    if m:
        h = int(m.group(1))
        if m.group(2) == "pm" and h != 12:
            h += 12
        elif m.group(2) == "am" and h == 12:
            h = 0
        return f"{h:02d}:00"

    return raw


def normalize_location(raw: str | None) -> str | None:
    """
    Convertit un lieu brut en nom normalisé via LOCATION_MAP.
    Fallback : title-case du texte original.
    """
    if not raw:
        return None
    key = raw.lower().strip()
    return LOCATION_MAP.get(key, raw.title())


def postprocess(raw: dict, text: str = "") -> dict:
    """
    Post-traitement complet du résultat NER brut.

    Étapes :
      1. Fallback regex pour time/date si champ absent
      2. Normalisation de chaque champ
      3. Calcul de missing_fields (destination, date, time)

    Args:
        raw  : {"destination", "departure", "date", "time"}  (valeurs brutes)
        text : texte original (pour fallback regex)

    Returns:
        dict normalisé + clé "missing_fields": list[str]
    """
    if text:
        for pattern, field in FALLBACK_RULES:
            if not raw.get(field):
                m = pattern.search(text)
                if m:
                    raw[field] = m.group(0)

    dep = normalize_location(raw.get("departure"))
    # Normaliser les variantes de casse de current_location
    if dep and dep.lower() == "current_location":
        dep = "current_location"

    result = {
        "destination": normalize_location(raw.get("destination")),
        "departure":   dep if dep else "current_location",
        "date":        normalize_date(raw.get("date")),
        "time":        normalize_time(raw.get("time")),
    }

    result["missing_fields"] = [
        f for f in ["destination", "date", "time"]
        if not result.get(f)
    ]

    return result