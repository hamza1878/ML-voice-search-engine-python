"""
MOVIROO — config/strict_normalization.py

Strict normalization engine for taxi booking entity extraction.

Rules:
  - Destination: fuzzy-match against KNOWN_LOCATIONS + LOCATION_ALIASES.
    Rejects truncated / unrecoverable tokens.
  - Date:  only today/tomorrow/weekdays/ISO dates. Garbage → None.
  - Time:  only valid formats (8h, 08:00, 20:30, semantic). Garbage → None.
  - Filler words stripped before processing.
  - Output: always JSON with destination, departure, date, time, missing_fields.
"""

import re
from datetime import date, timedelta
from difflib import get_close_matches

from config.knowledge import (
    LOCATION_ALIASES,
    KNOWN_LOCATIONS,
    TIME_TRIGGER_MAP,
    DATE_TRIGGER_MAP,
)

# ─────────────────────────────────────────────────────────────
# FILLER / NOISE WORDS — stripped before entity extraction
# ─────────────────────────────────────────────────────────────

FILLER_WORDS: set[str] = {
    # FR
    "je", "veux", "voudrais", "aller", "à", "au", "en", "un", "une",
    "le", "la", "les", "de", "du", "des", "pour", "s'il", "vous",
    "plaît", "svp", "réserver", "réservation", "prendre", "chercher",
    "j'aimerais", "j'ai", "besoin", "souhaite", "peux", "puis",
    # TN
    "nheb", "bch", "nemchi", "nroh", "lel", "fi", "men", "khodni",
    "mchini", "3aybni", "lazem", "tnajem", "tjibli",
    # EN
    "i", "want", "to", "go", "please", "need", "a", "the", "take",
    "me", "book", "get", "ride", "cab", "taxi",
    # AR
    "أريد", "أحتاج", "من", "فضلك", "خذني", "وصلني",
}

# ─────────────────────────────────────────────────────────────
# DATE — accepted keywords (from knowledge + local extras)
# ─────────────────────────────────────────────────────────────

_DATE_KEYWORDS: dict[str, str] = {
    **DATE_TRIGGER_MAP,
    # Extra dialectal variants
    "lioum":               "today",
    "tawwali":             "now",
    "ghodoa":              "tomorrow",
    "ghodwaa":             "tomorrow",
    "ghodwaaa":            "tomorrow",
    "el-jemaa el-jaya":    "next_friday",
    "jemaa":               "friday",
    "khamis":              "thursday",
    "ahad":                "sunday",
    "itnin":               "monday",
    "talata":              "tuesday",
    "arba3":               "wednesday",
    "sebt":                "saturday",
    "el-sebt":             "saturday",
    "el-lil":              "tonight",
    "aujourdhui":          "today",
    "apres-demain":        "day_after_tomorrow",
    "apres demain":        "day_after_tomorrow",
    "ce matin":            "today",
    "lundi prochain":      "next_monday",
    "vendredi prochain":   "next_friday",
    "dimanche prochain":   "next_sunday",
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
    "غداً":                "tomorrow",
    "مساء الجمعة":         "friday",
    "الاثنين القادم":      "next_monday",
    "الجمعة القادمة":      "next_friday",
}

_DATE_DELTA: dict[str, int] = {
    "today": 0, "now": 0, "tomorrow": 1,
    "day_after_tomorrow": 2, "tonight": 0,
}

_DAY_NAMES: dict[str, int] = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

_NEXT_DAY_NAMES: dict[str, int] = {
    f"next_{k}": v for k, v in _DAY_NAMES.items()
}

# Regex for numeric date formats
_DATE_NUMERIC_RE = re.compile(
    r"^(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{4}))?$"
)
_DATE_ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}$"
)

# Month name mappings for natural language date parsing
_MONTH_NAMES_FR: dict[str, int] = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12,
    "février": 2, "août": 8,
    # Common misspellings / dialectal variants
    "juan": 6,     # "juan" instead of "juin"
    "jull": 7,     # "jull" instead of "juillet"
    "juil": 7,     # truncated
    "aout": 8,     # already there
    "out": 8,      # "out" for août
    "sept": 9,     # truncated
    "oct": 10,     # truncated
    "nov": 11,     # truncated
    "dec": 12,     # truncated
}

_MONTH_NAMES_AR: dict[str, int] = {
    "جانفي": 1, "يناير": 1,
    "فيفري": 2, "فبراير": 2,
    "مارس": 3,
    "أفريل": 4, "افريل": 4, "إبريل": 4, "ابريل": 4,
    "ماي": 5, "مايو": 5,
    "جوان": 6, "يونيو": 6,
    "جويلية": 7, "يوليو": 7,
    "أوت": 8, "اوت": 8, "غشت": 8, "أغسطس": 8, "اغسطس": 8,
    "سبتمبر": 9, "septembre": 9,
    "أكتوبر": 10, "اكتوبر": 10,
    "نوفمبر": 11,
    "ديسمبر": 12, "ديسانبر": 12,
}

# Pattern: "15 juin", "1er juillet", "15 جوان", "1 جانفي"
_DATE_MONTH_NAME_RE = re.compile(
    r"(?:^|(?<=\s))(\d{1,2})(?:\s*er)?\s+([a-zA-Z\u0600-\u06ff]+)",
    re.IGNORECASE,
)

# ─────────────────────────────────────────────────────────────
# TIME — accepted keywords
# ─────────────────────────────────────────────────────────────

_TIME_KEYWORDS: dict[str, str] = {
    **TIME_TRIGGER_MAP,
    "fel sbeh":        "morning",
    "fel 3achiya":     "evening",
    "fel dhuhr":       "noon",
    "nouss el-lil":    "midnight",
    "el-lil":          "night",
    "apres-midi":      "afternoon",
    "après-midi":      "afternoon",
    "apres midi":      "afternoon",
    "minuit":          "midnight",
    "مساءً":           "evening",
    "منتصف الليل":     "midnight",
}

# Regex for valid time formats
_TIME_HM_RE   = re.compile(r"^(\d{1,2})h(\d{0,2})$")       # 8h, 18h30
_TIME_COLON_RE = re.compile(r"^(\d{1,2}):(\d{2})$")         # 14:00
_TIME_AMPM_RE  = re.compile(r"^(\d{1,2})\s*([AaPp][Mm])$")  # 8am, 10PM
_TIME_BARE_RE  = re.compile(r"^(\d{1,2})$")                  # bare "8" → 08:00

# ─────────────────────────────────────────────────────────────
# DIRECTIONAL PATTERNS — two-location extraction fallback
# ─────────────────────────────────────────────────────────────

# Pattern: <FROM_KW> <LOC_A> <TO_KW> <LOC_B>
# Captures (loc_a, loc_b) where loc_a=departure, loc_b=destination
_DIRECTION_PATTERNS: list[re.Pattern] = [
    # FR:  "de X vers Y", "de X à Y", "depuis X vers Y"
    re.compile(
        r"(?:de|depuis)\s+(.+?)\s+(?:vers|à|a|pour)\s+(.+?)(?:\s|$)",
        re.IGNORECASE,
    ),
    # EN:  "from X to Y"
    re.compile(
        r"(?:from)\s+(.+?)\s+(?:to)\s+(.+?)(?:\s|$)",
        re.IGNORECASE,
    ),
    # TN:  "men X lel Y", "min X lel Y"
    re.compile(
        r"(?:men|min)\s+(.+?)\s+(?:lel|l|il)\s+(.+?)(?:\s|$)",
        re.IGNORECASE,
    ),
    # AR:  "من X إلى Y"
    re.compile(
        r"(?:من)\s+(.+?)\s+(?:إلى|الى|ل)\s+(.+?)(?:\s|$)",
    ),
]

# Pattern: <PREP> <LOC_A> <TO_KW> <LOC_B>  (anchored by preposition)
# e.g. "à tunis vers hammamet"
_DIRECTION_PREP_TO: list[re.Pattern] = [
    # FR: "à X vers Y", "au X pour Y"
    re.compile(
        r"(?:à|a|au)\s+(.+?)\s+(?:vers|pour)\s+(.+?)(?:\s|$)",
        re.IGNORECASE,
    ),
]

# Directional keywords that signal "towards destination"
_TO_KEYWORDS = {"vers", "à", "a", "pour", "to", "lel", "l", "il", "إلى", "الى"}


def _find_all_locations_in_text(text: str) -> list[tuple[int, str]]:
    """
    Scan text for all recognizable location names (aliases + known locations).
    Returns list of (position, canonical_name) sorted by position.
    Skips current_location aliases.
    """
    lowered = text.lower()
    found: list[tuple[int, str]] = []
    seen: set[str] = set()

    # Sort aliases longest-first to prefer "la marsa" over "marsa"
    sorted_aliases = sorted(LOCATION_ALIASES.items(), key=lambda x: -len(x[0]))

    for alias, canonical in sorted_aliases:
        if canonical.lower() == "current_location":
            continue
        if canonical in seen:
            continue
        # Use word-boundary-like matching: preceded by start/space, followed by space/end/punct
        pat = r"(?:^|(?<=\s))" + re.escape(alias) + r"(?=\s|$|[,;.!?])"
        m = re.search(pat, lowered)
        if m:
            found.append((m.start(), canonical))
            seen.add(canonical)

    found.sort(key=lambda x: x[0])
    return found


def _clean_captured(raw: str) -> str:
    """Strip punctuation and extra whitespace from regex-captured groups."""
    return re.sub(r"[,;.!?\u060C\u061F]+", "", raw).strip()


def _extract_two_locations(text: str) -> tuple[str | None, str | None]:
    """
    Fallback: scan raw text for directional patterns with two locations.
    Returns (departure, destination) or (None, None) if no pattern matches.
    Both values are validated through strict_normalize_location.
    """
    lowered = text.lower().strip()

    # 1. Try explicit "from X to Y" patterns (most reliable)
    #    Use finditer to try ALL matches (in case first match has garbage in groups)
    for pat in _DIRECTION_PATTERNS:
        for m in pat.finditer(lowered):
            loc_a = strict_normalize_location(_clean_captured(m.group(1)))
            loc_b = strict_normalize_location(_clean_captured(m.group(2)))
            if loc_a and loc_b and loc_a != loc_b:
                return loc_a, loc_b

    # 1b. Try reversed TN: "lel/il Y men X" → departure=X, destination=Y
    for m in re.finditer(
        r"(?:lel|il)\s+(.+?)\s+(?:men|min)\s+(.+?)(?:\s|$)",
        lowered, re.IGNORECASE,
    ):
        loc_dest = strict_normalize_location(_clean_captured(m.group(1)))
        loc_dep = strict_normalize_location(_clean_captured(m.group(2)))
        if loc_dep and loc_dest and loc_dep != loc_dest:
            return loc_dep, loc_dest  # swapped: dep, dest

    # 2. Try "à X vers Y" patterns (preposition-anchored)
    for pat in _DIRECTION_PREP_TO:
        for m in pat.finditer(lowered):
            loc_a = strict_normalize_location(_clean_captured(m.group(1)))
            loc_b = strict_normalize_location(_clean_captured(m.group(2)))
            if loc_a and loc_b and loc_a != loc_b:
                return loc_a, loc_b

    # 3. Final fallback: find all known locations in text by name
    locs = _find_all_locations_in_text(text)
    if len(locs) >= 2:
        # Two distinct locations found — check for directional keyword between them
        pos1, name1 = locs[0]
        pos2, name2 = locs[1]
        between = lowered[pos1:pos2].split()
        has_direction = any(w in _TO_KEYWORDS for w in between)
        if has_direction:
            # "X <vers/to> Y" → X=departure, Y=destination
            return name1, name2
        # Even without directional keyword, if 2 locations exist:
        # first mentioned = departure, second = destination
        return name1, name2

    return None, None


# ─────────────────────────────────────────────────────────────
# LOCATION — fuzzy matching pool
# ─────────────────────────────────────────────────────────────

# All valid location strings (lowered) for fuzzy matching
_LOCATION_POOL: list[str] = list({
    k.lower() for k in LOCATION_ALIASES
} | {
    v.lower() for v in LOCATION_ALIASES.values()
} | {
    loc.lower() for loc in KNOWN_LOCATIONS
})

# Minimum token length for location fuzzy matching (reject "tu", "s", etc.)
_MIN_LOCATION_LEN = 3

# Fuzzy match cutoff (0-1). Higher = stricter.
_FUZZY_CUTOFF = 0.65


# ─────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────

def strip_fillers(text: str) -> str:
    """Remove filler/noise words, keeping only meaningful tokens."""
    tokens = text.strip().split()
    kept = [t for t in tokens if t.lower() not in FILLER_WORDS]
    return " ".join(kept) if kept else text


def strict_normalize_location(raw: str | None) -> str | None:
    """
    Normalize a location token.

    1. Exact match in LOCATION_ALIASES → canonical name.
    2. Fuzzy match against known locations (cutoff=0.65).
    3. Reject if token is too short (<3 chars) and no match.
    4. Return None if unrecoverable.
    """
    if not raw:
        return None
    key = raw.lower().strip()

    # Rule: reject empty or purely numeric
    if not key or key.isnumeric():
        return None

    # 1. Exact alias lookup
    if key in LOCATION_ALIASES:
        return LOCATION_ALIASES[key]

    # 2. Check if it already matches a known location (case-insensitive)
    for loc in KNOWN_LOCATIONS:
        if key == loc.lower():
            return loc

    # 3. Reject very short tokens that didn't match exactly
    if len(key) < _MIN_LOCATION_LEN:
        return None

    # 4. Fuzzy match against the pool
    matches = get_close_matches(key, _LOCATION_POOL, n=1, cutoff=_FUZZY_CUTOFF)
    if matches:
        best = matches[0]
        # Resolve back to canonical name
        if best in LOCATION_ALIASES:
            return LOCATION_ALIASES[best]
        # Find in KNOWN_LOCATIONS by lower match
        for loc in KNOWN_LOCATIONS:
            if loc.lower() == best:
                return loc
        return best.title()

    # 5. No match → None (strict: never return garbage)
    return None


def strict_normalize_date(raw: str | None) -> str | None:
    """
    Normalize a date token. Returns ISO date or None.

    Accepted:
      - Keywords: today, tomorrow, demain, ghodwa, weekdays, etc.
      - ISO format: YYYY-MM-DD
      - Numeric: DD/MM, DD-MM-YYYY
    Rejected:
      - Random words: "allrez", "tunisia", "8h"
      - Anything that doesn't resolve to a real date.
    """
    if not raw:
        return None

    key = raw.lower().strip()
    today = date.today()

    # Quick rejection: looks like a time token, not a date
    if _TIME_HM_RE.match(key) or _TIME_AMPM_RE.match(key):
        return None

    # Already ISO?
    if _DATE_ISO_RE.match(key):
        try:
            parts = key.split("-")
            date(int(parts[0]), int(parts[1]), int(parts[2]))
            return key
        except ValueError:
            return None

    # Keyword lookup
    mapped = _DATE_KEYWORDS.get(key)
    if mapped:
        if mapped in _DATE_DELTA:
            return (today + timedelta(days=_DATE_DELTA[mapped])).isoformat()
        if mapped == "tonight":
            return today.isoformat()
        if mapped in _DAY_NAMES:
            ahead = (_DAY_NAMES[mapped] - today.weekday()) % 7
            if ahead == 0:
                ahead = 7
            return (today + timedelta(days=ahead)).isoformat()
        if mapped in _NEXT_DAY_NAMES:
            target = _NEXT_DAY_NAMES[mapped]
            ahead = (target - today.weekday()) % 7
            if ahead == 0:
                ahead = 7
            return (today + timedelta(days=ahead)).isoformat()

    # Natural language: "15 juin", "1er juillet", "15 جوان", "1 جانفي"
    m = _DATE_MONTH_NAME_RE.search(key)
    if m:
        day = int(m.group(1))
        month_name = m.group(2).lower().strip()
        month = _MONTH_NAMES_FR.get(month_name) or _MONTH_NAMES_AR.get(month_name)
        if month and 1 <= day <= 31:
            try:
                d = date(today.year, month, day)
                # If the date is in the past, assume next year
                if d < today:
                    d = date(today.year + 1, month, day)
                return d.isoformat()
            except ValueError:
                pass

    # Numeric DD/MM or DD/MM/YYYY
    m = _DATE_NUMERIC_RE.match(key)
    if m:
        try:
            d = date(
                int(m.group(3) or today.year),
                int(m.group(2)),
                int(m.group(1)),
            )
            return d.isoformat()
        except ValueError:
            return None

    # Bare number 1-31 → day of current month
    m = re.match(r"^(\d{1,2})$", key)
    if m:
        day = int(m.group(1))
        if 1 <= day <= 31:
            try:
                d = date(today.year, today.month, day)
                return d.isoformat()
            except ValueError:
                # Day doesn't exist in current month (e.g., Feb 30)
                pass

    # STRICT: anything else → None (garbage rejected)
    return None


def strict_normalize_time(raw: str | None) -> str | None:
    """
    Normalize a time token. Returns HH:MM or semantic label, or None.

    Accepted:
      - Keywords: morning, soir, midi, sbeh, 3achiya, etc.
      - Formats: 8h, 8h30, 08:00, 20:30, 8am, 10PM
      - Bare hour: "8" → "08:00"
    Rejected:
      - Random words: "allrez", "tunisia", "demain"
    """
    if not raw:
        return None

    key = raw.lower().strip()

    # Keyword lookup
    if key in _TIME_KEYWORDS:
        return _TIME_KEYWORDS[key]

    # 18h / 8h30
    m = _TIME_HM_RE.match(key)
    if m:
        h = int(m.group(1))
        mn = int(m.group(2) or 0)
        if 0 <= h <= 23 and 0 <= mn <= 59:
            return f"{h:02d}:{mn:02d}"
        return None

    # 14:00
    m = _TIME_COLON_RE.match(key)
    if m:
        h = int(m.group(1))
        mn = int(m.group(2))
        if 0 <= h <= 23 and 0 <= mn <= 59:
            return f"{h:02d}:{m.group(2)}"
        return None

    # 8am / 10PM
    m = _TIME_AMPM_RE.match(key)
    if m:
        h = int(m.group(1))
        if m.group(2).lower() == "pm" and h != 12:
            h += 12
        elif m.group(2).lower() == "am" and h == 12:
            h = 0
        if 0 <= h <= 23:
            return f"{h:02d}:00"
        return None

    # Bare number: "8" → "08:00" (only if 0-23)
    m = _TIME_BARE_RE.match(key)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return f"{h:02d}:00"
        return None

    # STRICT: anything else → None
    return None


def strict_postprocess(raw: dict, text: str = "") -> dict:
    """
    Strict post-processing of NER output.

    Steps:
      1. Strip filler words from text for fallback regex.
      2. Normalize each entity with strict rules.
      3. Cross-validate: reject date if it's actually a location, etc.
      4. Compute missing_fields.

    Returns:
        {
            "destination": str | None,
            "departure":   str | None,
            "date":        str | None,
            "time":        str | None,
            "missing_fields": list[str],
        }
    """
    # Fallback regex on cleaned text
    if text:
        cleaned = strip_fillers(text)
        # Try to extract date from text FIRST (before time steals the number)
        if not raw.get("date"):
            # ISO: YYYY-MM-DD
            m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", cleaned)
            if not m:
                # DD/MM or DD/MM/YYYY or DD-MM or DD-MM-YYYY
                m = re.search(r"\b(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{4})?)\b", cleaned)
            if not m:
                # Natural language: "15 juin", "1er juillet", "15 جوان"
                m = _DATE_MONTH_NAME_RE.search(cleaned)
            if not m:
                # Date keywords in text
                for kw in _DATE_KEYWORDS:
                    if kw in cleaned.lower():
                        m = type('M', (), {'group': lambda self, n=0: kw})()
                        break
            if m:
                raw["date"] = m.group(0)
        # Try to extract time from text if missing
        if not raw.get("time"):
            m = re.search(
                r"\b(\d{1,2}h\d{0,2}|\d{1,2}:\d{2}|\d{1,2}\s*[AaPp][Mm])\b",
                cleaned,
            )
            if m:
                raw["time"] = m.group(0)

    # Normalize
    dest = strict_normalize_location(raw.get("destination"))
    dep  = strict_normalize_location(raw.get("departure"))
    dt   = strict_normalize_date(raw.get("date"))
    tm   = strict_normalize_time(raw.get("time"))

    # Cross-validate: if "date" raw value resolves to a location, nullify date
    raw_date = (raw.get("date") or "").lower().strip()
    if raw_date and strict_normalize_location(raw_date) and not dt:
        dt = None  # was a location, not a date

    # Cross-validate: if "time" raw value resolves to a date keyword, nullify time
    raw_time = (raw.get("time") or "").lower().strip()
    if raw_time and raw_time in _DATE_KEYWORDS and not tm:
        tm = None

    # ── Dedup: same location in both fields → keep only destination ──
    # When NER tags a single location as both departure and destination,
    # reset departure so it defaults to current_location later.
    if dest and dep and dest == dep and dep.lower() != "current_location":
        dep = None

    # ── Directional fallback: extract two locations from raw text ──
    # Activates when NER missed departure (dep is None) and text has
    # directional patterns like "de X vers Y" / "from X to Y"
    if text and not dep:
        fb_dep, fb_dest = _extract_two_locations(text)
        if fb_dep and fb_dest:
            dep = fb_dep
            # Only override dest if NER also missed it
            if not dest:
                dest = fb_dest
            # If NER got dest but it matches fb_dep (swapped), fix it
            elif dest == fb_dep:
                dest = fb_dest

    # ── Single-location fallback ──
    # Case A: NER found dest but not dep → other location in text = departure
    # Case B: NER found nothing → first location in text = destination
    if text and (not dep or not dest):
        locs = _find_all_locations_in_text(text)
        if dest and not dep:
            for _, name in locs:
                if name != dest:
                    dep = name
                    break
        elif not dest:
            for _, name in locs:
                dest = name
                break

    # Departure defaults to current_location
    if dep and dep.lower() == "current_location":
        dep = "current_location"
    if not dep:
        dep = "current_location"

    result = {
        "destination":    dest,
        "departure":      dep,
        "date":           dt,
        "time":           tm,
        "missing_fields": [],
    }

    result["missing_fields"] = [
        f for f in ["destination", "date", "time"]
        if not result.get(f)
    ]

    return result
