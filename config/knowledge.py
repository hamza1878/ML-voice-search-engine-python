"""
MOVIROO — config/knowledge.py

Source de vérité unique pour :
  - TRIGGER_WORDS   : mots déclencheurs par champ et par langue
  - LOCATION_ALIASES: alias → nom normalisé (tous les dialectes)
  - KNOWN_LOCATIONS : liste des villes reconnues
  - REGEX_PATTERNS  : patterns regex pour time et date
  - TIME_RANGES     : plages horaires sémantiques → HH:MM
  - TRAINING_EXAMPLES : exemples canoniques (gold standard)

Tous les autres modules importent depuis ce fichier.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────
# TYPE ALIAS
# ─────────────────────────────────────────────────────────────

TriggerEntry = dict[str, str]   # {"word": ..., "lang": ..., "normalized": ...}


# ─────────────────────────────────────────────────────────────
# TRIGGER WORDS — DESTINATION
# ─────────────────────────────────────────────────────────────

DESTINATION_TRIGGERS: list[TriggerEntry] = [
    # TN
    {"word": "wein",           "lang": "TN",    "normalized": "where to"},
    {"word": "nemchi",         "lang": "TN",    "normalized": "go"},
    {"word": "bch nemchi",     "lang": "TN",    "normalized": "going to"},
    {"word": "khodni",         "lang": "TN",    "normalized": "pick me up"},
    {"word": "fi",             "lang": "TN",    "normalized": "at"},
    {"word": "matar",          "lang": "TN",    "normalized": "airport"},
    {"word": "mahatta",        "lang": "TN",    "normalized": "station"},
    {"word": "wust el-bled",   "lang": "TN",    "normalized": "city center"},
    # FR
    {"word": "où",             "lang": "FR",    "normalized": "where to"},
    {"word": "aller à",        "lang": "FR",    "normalized": "go to"},
    {"word": "vers",           "lang": "FR",    "normalized": "towards"},
    {"word": "je dois aller",  "lang": "FR",    "normalized": "go to"},
    {"word": "arriver à",      "lang": "FR",    "normalized": "arrive at"},
    {"word": "destination",    "lang": "FR/EN", "normalized": "destination"},
    {"word": "aéroport",       "lang": "FR",    "normalized": "airport"},
    {"word": "gare",           "lang": "FR",    "normalized": "station"},
    # EN
    {"word": "where",          "lang": "EN",    "normalized": "where to"},
    {"word": "go to",          "lang": "EN",    "normalized": "go to"},
    {"word": "take me to",     "lang": "EN",    "normalized": "go to"},
    {"word": "drop me at",     "lang": "EN",    "normalized": "drop at"},
    {"word": "deliver me to",  "lang": "EN",    "normalized": "go to"},
    # AR
    {"word": "وين",            "lang": "AR",    "normalized": "where to"},
    {"word": "نروح",           "lang": "AR",    "normalized": "go to"},
    {"word": "إلى",            "lang": "AR",    "normalized": "to"},
]

# Lookup rapide : word.lower() → normalized
DESTINATION_TRIGGER_MAP: dict[str, str] = {
    e["word"].lower(): e["normalized"]
    for e in DESTINATION_TRIGGERS
}
DATE_KEYWORDS = {
    "demain": "tomorrow",
    "ghodwa": "tomorrow",
    "tomorrow": "tomorrow"
}


DEPARTURE_TRIGGERS: list[TriggerEntry] = [
    # TN
    {"word": "min",              "lang": "TN", "normalized": "from"},
    {"word": "men 3andi",        "lang": "TN", "normalized": "from my place"},
    {"word": "khodni",           "lang": "TN", "normalized": "pick me up"},
    {"word": "mchini",           "lang": "TN", "normalized": "pick me up"},
    {"word": "hne",              "lang": "TN", "normalized": "current_location"},
    {"word": "3andi",            "lang": "TN", "normalized": "my place"},
    {"word": "beit",             "lang": "TN", "normalized": "home"},
    {"word": "dar",              "lang": "TN", "normalized": "home"},
    {"word": "funduk",           "lang": "TN", "normalized": "hotel"},
    # FR
    {"word": "de",               "lang": "FR", "normalized": "from"},
    {"word": "depuis",           "lang": "FR", "normalized": "from"},
    {"word": "ici",              "lang": "FR", "normalized": "current_location"},
    {"word": "ma position",      "lang": "FR", "normalized": "current_location"},
    {"word": "bureau",           "lang": "FR", "normalized": "office"},
    {"word": "l'hotel",          "lang": "FR", "normalized": "hotel"},
    {"word": "point de départ",  "lang": "FR", "normalized": "departure point"},
    # EN
    {"word": "from",             "lang": "EN", "normalized": "from"},
    {"word": "starting from",    "lang": "EN", "normalized": "from"},
    {"word": "pick me up",       "lang": "EN", "normalized": "pickup"},
    {"word": "current location", "lang": "EN", "normalized": "current_location"},
    # AR
    {"word": "من",               "lang": "AR", "normalized": "from"},
    {"word": "هنا",              "lang": "AR", "normalized": "current_location"},
    {"word": "مكتب",             "lang": "AR", "normalized": "office"},
    {"word": "maktab",           "lang": "AR", "normalized": "office"},
]

DEPARTURE_DEFAULT = "current_location"

DEPARTURE_TRIGGER_MAP: dict[str, str] = {
    e["word"].lower(): e["normalized"]
    for e in DEPARTURE_TRIGGERS
}


# ─────────────────────────────────────────────────────────────
# TRIGGER WORDS — TIME
# ─────────────────────────────────────────────────────────────

TIME_TRIGGERS: list[TriggerEntry] = [
    # TN
    {"word": "3achiya",       "lang": "TN", "normalized": "evening"},
    {"word": "sbeh",          "lang": "TN", "normalized": "morning"},
    {"word": "dhuhr",         "lang": "TN", "normalized": "noon"},
    {"word": "leyl",          "lang": "TN", "normalized": "night"},
    {"word": "nouss el-lil",  "lang": "TN", "normalized": "midnight"},
    {"word": "ba3d dhuhr",    "lang": "TN", "normalized": "afternoon"},
    {"word": "fel sbeh",      "lang": "TN", "normalized": "morning"},
    {"word": "fel 3achiya",   "lang": "TN", "normalized": "evening"},
    {"word": "sa3a",          "lang": "TN", "normalized": "hour"},
    {"word": "wa9tech",       "lang": "TN", "normalized": "what time"},
    # FR
    {"word": "soir",          "lang": "FR", "normalized": "evening"},
    {"word": "matin",         "lang": "FR", "normalized": "morning"},
    {"word": "midi",          "lang": "FR", "normalized": "noon"},
    {"word": "nuit",          "lang": "FR", "normalized": "night"},
    {"word": "après-midi",    "lang": "FR", "normalized": "afternoon"},
    {"word": "tôt le matin",  "lang": "FR", "normalized": "early morning"},
    {"word": "heure",         "lang": "FR", "normalized": "hour"},
    {"word": "à quelle heure","lang": "FR", "normalized": "what time"},
    # EN
    {"word": "evening",       "lang": "EN", "normalized": "evening"},
    {"word": "morning",       "lang": "EN", "normalized": "morning"},
    {"word": "noon",          "lang": "EN", "normalized": "noon"},
    {"word": "night",         "lang": "EN", "normalized": "night"},
    {"word": "afternoon",     "lang": "EN", "normalized": "afternoon"},
    {"word": "what time",     "lang": "EN", "normalized": "what time"},
    # AR
    {"word": "masa",          "lang": "AR", "normalized": "evening"},
    {"word": "sabah",         "lang": "AR", "normalized": "morning"},
    {"word": "layl",          "lang": "AR", "normalized": "night"},
    {"word": "مساء",          "lang": "AR", "normalized": "evening"},
    {"word": "صباحا",         "lang": "AR", "normalized": "morning"},
    {"word": "الصباح",        "lang": "AR", "normalized": "morning"},
    {"word": "المساء",        "lang": "AR", "normalized": "evening"},
    {"word": "الليل",         "lang": "AR", "normalized": "night"},
    {"word": "الظهر",         "lang": "AR", "normalized": "noon"},
]

TIME_TRIGGER_MAP: dict[str, str] = {
    e["word"].lower(): e["normalized"]
    for e in TIME_TRIGGERS
}

# Regex pour les heures numériques (dans l'ordre de priorité)
TIME_REGEX_PATTERNS: list[dict[str, str]] = [
    {"pattern": r"\d{1,2}h\d{0,2}",          "example": "18h, 8h30",    "output": "HH:MM"},
    {"pattern": r"\d{1,2}:\d{2}",             "example": "14:00",        "output": "HH:MM"},
    {"pattern": r"\d{1,2}h du (matin|soir)",  "example": "9h du matin",  "output": "HH:MM"},
]

# Plages horaires sémantiques
TIME_RANGES: dict[str, str] = {
    "morning":        "06:00-11:59",
    "noon":           "12:00-13:59",
    "afternoon":      "14:00-17:59",
    "evening":        "18:00-21:59",
    "night":          "22:00-05:59",
    "early morning":  "05:00-07:59",
    "midnight":       "00:00",
}


# ─────────────────────────────────────────────────────────────
# TRIGGER WORDS — DATE
# ─────────────────────────────────────────────────────────────

DATE_TRIGGERS: list[TriggerEntry] = [
    # TN
    {"word": "lyoum",              "lang": "TN", "normalized": "today"},
    {"word": "ghodwa",             "lang": "TN", "normalized": "tomorrow"},
    {"word": "ba3d ghodwa",        "lang": "TN", "normalized": "day_after_tomorrow"},
    {"word": "tawwa",              "lang": "TN", "normalized": "now"},
    {"word": "el-jemaa",           "lang": "TN", "normalized": "friday"},
    {"word": "el-khamis",          "lang": "TN", "normalized": "thursday"},
    {"word": "el-ahad",            "lang": "TN", "normalized": "sunday"},
    {"word": "el-itnin",           "lang": "TN", "normalized": "monday"},
    {"word": "el-talata",          "lang": "TN", "normalized": "tuesday"},
    {"word": "el-arba3",           "lang": "TN", "normalized": "wednesday"},
    {"word": "el-jom3a el-jaya",   "lang": "TN", "normalized": "next_friday"},
    # FR
    {"word": "aujourd'hui",        "lang": "FR", "normalized": "today"},
    {"word": "demain",             "lang": "FR", "normalized": "tomorrow"},
    {"word": "après-demain",       "lang": "FR", "normalized": "day_after_tomorrow"},
    {"word": "maintenant",         "lang": "FR", "normalized": "now"},
    {"word": "ce soir",            "lang": "FR", "normalized": "tonight"},
    {"word": "lundi",              "lang": "FR", "normalized": "monday"},
    {"word": "mardi",              "lang": "FR", "normalized": "tuesday"},
    {"word": "mercredi",           "lang": "FR", "normalized": "wednesday"},
    {"word": "jeudi",              "lang": "FR", "normalized": "thursday"},
    {"word": "vendredi",           "lang": "FR", "normalized": "friday"},
    {"word": "samedi",             "lang": "FR", "normalized": "saturday"},
    {"word": "dimanche",           "lang": "FR", "normalized": "sunday"},
    {"word": "cette semaine",      "lang": "FR", "normalized": "this_week"},
    {"word": "semaine prochaine",  "lang": "FR", "normalized": "next_week"},
    # EN
    {"word": "today",              "lang": "EN", "normalized": "today"},
    {"word": "tomorrow",           "lang": "EN", "normalized": "tomorrow"},
    {"word": "day after tomorrow", "lang": "EN", "normalized": "day_after_tomorrow"},
    {"word": "now",                "lang": "EN", "normalized": "now"},
    {"word": "tonight",            "lang": "EN", "normalized": "tonight"},
    {"word": "this friday",        "lang": "EN", "normalized": "friday"},
    {"word": "next week",          "lang": "EN", "normalized": "next_week"},
    {"word": "weekend",            "lang": "EN", "normalized": "weekend"},
    # AR
    {"word": "اليوم",              "lang": "AR", "normalized": "today"},
    {"word": "غدا",                "lang": "AR", "normalized": "tomorrow"},
    {"word": "بعد غد",             "lang": "AR", "normalized": "day_after_tomorrow"},
    {"word": "الآن",               "lang": "AR", "normalized": "now"},
    {"word": "الجمعة",             "lang": "AR", "normalized": "friday"},
    {"word": "الخميس",             "lang": "AR", "normalized": "thursday"},
    {"word": "الاثنين",            "lang": "AR", "normalized": "monday"},
    {"word": "الأحد",              "lang": "AR", "normalized": "sunday"},
    {"word": "الأربعاء",           "lang": "AR", "normalized": "wednesday"},
    {"word": "السبت",              "lang": "AR", "normalized": "saturday"},
    {"word": "الثلاثاء",           "lang": "AR", "normalized": "tuesday"},
]

DATE_TRIGGER_MAP: dict[str, str] = {
    e["word"].lower(): e["normalized"]
    for e in DATE_TRIGGERS
}

# Month names for date normalization (mapped to month numbers)
MONTH_NAMES_FR: dict[str, int] = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
}

MONTH_NAMES_AR: dict[str, int] = {
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

# Regex pour les dates numériques
DATE_REGEX_PATTERNS: list[dict[str, str]] = [
    {"pattern": r"le \d{1,2}",           "example": "le 15",       "output": "YYYY-MM-DD"},
    {"pattern": r"\d{1,2}/\d{1,2}",      "example": "15/04",       "output": "YYYY-MM-DD"},
    {"pattern": r"\d{4}-\d{2}-\d{2}",    "example": "2025-04-15",  "output": "YYYY-MM-DD"},
]


# ─────────────────────────────────────────────────────────────
# LOCATION ALIASES
# ─────────────────────────────────────────────────────────────

# Tous les alias → nom normalisé (majuscule canonique)
LOCATION_ALIASES: dict[str, str] = {
    # Hammamet
    "7amaamt":        "Hammamet",
    "hamamet":        "Hammamet",
    "hammamet":       "Hammamet",
    "hammed":         "Hammamet",
    "hammam":         "Hammamet",
    "hammet":         "Hammamet",
    "hamet":          "Hammamet",
    "الحمامات":       "Hammamet",
    "حمامات":         "Hammamet",
    "yasmine hammamet": "Yasmine Hammamet",
    # Sousse
    "sousse":         "Sousse",
    "soussa":         "Sousse",
    "سوسة":           "Sousse",
    # Sfax
    "sfax":           "Sfax",
    "صفاقس":          "Sfax",
    # Tunis
    "tunis":          "Tunis",
    "tunise":         "Tunis",
    "tnis":           "Tunis",
    "touns":          "Tunis",
    "il touns":       "Tunis",
    "تونس":           "Tunis",
    # Monastir
    "monastir":       "Monastir",
    "المنستير":       "Monastir",
    # Nabeul
    "nabeul":         "Nabeul",
    "نابل":           "Nabeul",
    # Bizerte
    "bizerte":        "Bizerte",
    "بنزرت":          "Bizerte",
    # Kairouan
    "kairouan":       "Kairouan",
    "القيروان":       "Kairouan",
    # Djerba
    "djerba":         "Djerba",
    "جربة":           "Djerba",
    # Zones Tunis
    "la marsa":       "La Marsa",
    "marsa":          "La Marsa",
    "المرسى":         "La Marsa",
    "carthage":       "Carthage",
    "قرطاج":          "Carthage",
    "ennasr":         "Ennasr",
    "lac":            "Lac",
    "le lac":         "Lac",
    "البحيرة":        "Lac",
    "le centre":      "City Center",
    "le centre-ville":"City Center",
    "centre ville":   "City Center",
    "centre":         "City Center",
    "center":         "City Center",
    "city center":    "City Center",
    "downtown":       "City Center",
    "وسط المدينة":    "City Center",
    "wust el-bled":   "City Center",
    # Transport
    "matar":           "Airport",
    "matar carthage":  "Tunis Airport",
    "aeroport":        "Airport",
    "airport":         "Airport",
    "l'aéroport":      "Airport",
    "l aeroport":      "Airport",
    "the airport":     "Airport",
    "المطار":          "Airport",
    "gare":            "Train Station",
    "la gare":         "Train Station",
    "mahatta":         "Train Station",
    "station":         "Train Station",
    "the station":     "Train Station",
    "the train station":"Train Station",
    "المحطة":          "Train Station",
    "محطة القطار":     "Train Station",
    # Lieux génériques
    "funduk":          "Hotel",
    "hotel":           "Hotel",
    "the hotel":       "Hotel",
    "mon hotel":       "Hotel",
    "mon hôtel":       "Hotel",
    "الفندق":          "Hotel",
    "beit":            "Home",
    "dar":             "Home",
    "البيت":           "Home",
    "المنزل":          "Home",
    "home":            "Home",
    "house":           "Home",
    "maison":          "Home",
    "mon domicile":    "Home",
    "bureau":          "Office",
    "maktab":          "Office",
    "el-maktab":       "Office",
    "المكتب":          "Office",
    "office":          "Office",
    "mon bureau":      "Office",
    "my office":       "Office",
    "hospital":        "Hospital",
    "مستشفى":          "Hospital",
    "هنا":              "current_location",
    "hne":              "current_location",
    "ici":              "current_location",
    "here":             "current_location",
    "ma position":      "current_location",
    "current location": "current_location",
    "current_location": "current_location",   
}

KNOWN_LOCATIONS: list[str] = [
    "Tunis", "Hammamet", "Sfax", "Sousse", "Nabeul", "Monastir",
    "Djerba", "La Marsa", "Bizerte", "Kairouan", "Carthage",
    "Gabès", "Gafsa", "Tozeur", "Sidi Bou Said", "Ennasr", "Lac",
    "Ariana", "Ben Arous", "Manouba", "Zaghouan", "Béja", "Jendouba",
    "Kef", "Siliana", "Mahdia", "Kasserine", "Sidi Bouzid", "Médenine",
    "Tataouine", "Kébili", "Sidi Thabet", "El Aouina", "Gammarth",
    "Yasmine Hammamet", "Tunis Airport", "Train Station", "Airport",
    "City Center", "Hotel", "Home", "Office", "Hospital",
]


GOLD_EXAMPLES: list[dict] = [
    {
        "input":  "nheb nemchi hammamet ghodwa 3achiya",
        "lang":   "TN",
        "labels": {
            "destination": "Hammamet",
            "departure":   "current_location",
            "date":        "tomorrow",       # normalisé en ISO par postprocess
            "time":        "evening",
        },
    },
    {
        "input":  "je veux aller à tunis",
        "lang":   "FR",
        "labels": {
            "destination": "Tunis",
            "departure":   "current_location",
            "date":        None,
            "time":        None,
        },
    },
    {
        "input":  "I need a taxi from sfax to sousse tomorrow at 8h30",
        "lang":   "EN",
        "labels": {
            "destination": "Sousse",
            "departure":   "Sfax",
            "date":        "tomorrow",
            "time":        "08:30",
        },
    },
    {
        "input":  "khodni lel matar tawwa",
        "lang":   "TN",
        "labels": {
            "destination": "Airport",
            "departure":   "current_location",
            "date":        "today",
            "time":        None,             # "tawwa" → date=now, pas time
        },
    },
    {
        "input":  "réserver un taxi demain matin de la marsa vers le centre",
        "lang":   "FR",
        "labels": {
            "destination": "City Center",
            "departure":   "La Marsa",
            "date":        "tomorrow",
            "time":        "morning",
        },
    },
    {
        "input":  "bch nemchi sousse el-jemaa fel sbeh",
        "lang":   "TN",
        "labels": {
            "destination": "Sousse",
            "departure":   "current_location",
            "date":        "friday",
            "time":        "morning",
        },
    },
    {
        "input":  "take me to the airport tonight at 22h",
        "lang":   "EN",
        "labels": {
            "destination": "Airport",
            "departure":   "current_location",
            "date":        "tonight",
            "time":        "22:00",
        },
    },
    {
        "input":  "من هنا إلى سوسة غداً في المساء",
        "lang":   "AR",
        "labels": {
            "destination": "Sousse",
            "departure":   "current_location",
            "date":        "tomorrow",
            "time":        "evening",
        },
    },
    {
        "input":  "nemchi sfax min el-maktab el-khamis ba3d dhuhr",
        "lang":   "TN",
        "labels": {
            "destination": "Sfax",
            "departure":   "Office",
            "date":        "thursday",
            "time":        "afternoon",
        },
    },
    {
        "input":  "aller de bizerte à nabeul mercredi à 14h00",
        "lang":   "FR",
        "labels": {
            "destination": "Nabeul",
            "departure":   "Bizerte",
            "date":        "wednesday",
            "time":        "14:00",
        },
    },
]


# ─────────────────────────────────────────────────────────────
# HELPERS — extraction des markers pour detect_language
# ─────────────────────────────────────────────────────────────

def get_lang_markers() -> dict[str, list[str]]:
    """
    Extrait les mots déclencheurs par langue depuis toutes les listes
    de triggers. Utilisé par detect_language() dans dialog.py.

    Retourne {lang: [word, ...]} en minuscules.
    """
    buckets: dict[str, list[str]] = {"TN": [], "FR": [], "EN": [], "AR": []}
    all_triggers = (
        DESTINATION_TRIGGERS
        + DEPARTURE_TRIGGERS
        + TIME_TRIGGERS
        + DATE_TRIGGERS
    )
    for entry in all_triggers:
        langs = entry["lang"].split("/")   # gère "FR/EN"
        for lang in langs:
            lang = lang.strip()
            if lang in buckets:
                buckets[lang].append(entry["word"].lower())
    return buckets


# Pré-calculé une fois à l'import pour des détections rapides
LANG_MARKERS: dict[str, list[str]] = get_lang_markers()