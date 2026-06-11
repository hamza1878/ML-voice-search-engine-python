"""
MOVIROO — config/pools.py
Centralise toutes les listes de valeurs par langue.
"""

# ─────────────────────────────────────────────────────────────
# DESTINATIONS
# ─────────────────────────────────────────────────────────────

DESTINATIONS: dict[str, list[str]] = {
    "TN": [
        "hammamet", "sousse", "sfax", "monastir", "nabeul", "bizerte",
        "kairouan", "djerba", "matar", "gare", "tunis", "ariana", "ben arous",
        "manouba", "zaghouan", "beja", "jendouba", "kef", "siliana", "mahdia",
        "kasserine", "sidi bouzid", "gabes", "medenine", "tataouine", "kebili",
        "tozeur", "gafsa", "sidi thabet", "carthage", "el aouina", "la marsa",
        "sidi bou said", "gammarth", "lac", "centre ville", "cite olimpik",
        "bardo", "ezzouhour", "mrezga", "yasmine hammamet",
    ],
    "FR": [
        "hammamet", "sousse", "sfax", "monastir", "nabeul", "bizerte",
        "kairouan", "djerba", "l'aéroport", "l aeroport", "la gare",
        "tunis", "ariana", "ben arous", "manouba", "zaghouan", "béja",
        "jendouba", "le kef", "siliana", "mahdia", "kasserine", "sidi bouzid",
        "gabès", "médenine", "tataouine", "kébili", "tozeur", "gafsa",
        "sidi thabet", "carthage", "el aouina", "la marsa", "sidi bou saïd",
        "gammarth", "le lac", "le centre-ville", "le centre", "la cité olympique",
        "le bardo", "ez-zouhour", "mrezga", "yasmine hammamet",
    ],
    "EN": [
        "hammamet", "sousse", "sfax", "monastir", "nabeul", "bizerte",
        "kairouan", "djerba", "the airport", "the station", "the train station",
        "tunis", "ariana", "ben arous", "manouba", "zaghouan", "beja",
        "jendouba", "le kef", "siliana", "mahdia", "kasserine", "sidi bouzid",
        "gabes", "medenine", "tataouine", "kebili", "tozeur", "gafsa",
        "sidi thabet", "carthage", "el aouina", "la marsa", "sidi bou said",
        "gammarth", "the lake", "downtown", "city center", "the olympic city",
        "the bardo", "ez-zouhour", "mrezga", "yasmine hammamet",
    ],
    "AR": [
        "حمام الأنف", "سوسة", "صفاقس", "المنستير", "نابل", "بنزرت",
        "القيروان", "جربة", "المطار", "محطة القطار", "تونس", "أريانة",
        "بن عروس", "منوبة", "زغوان", "باجة", "جندوبة", "الكاف",
        "سليانة", "المهدية", "القصرين", "سيدي بوزيد", "قابس", "مدنين",
        "تطاوين", "قبلي", "توزر", "قفصة", "سيدي ثابت", "قرطاج",
        "العوينة", "المرسى", "سيدي بوسعيد", "قمرت", "البحيرة",
        "وسط المدينة", "المدينة الأولمبية", "باردو", "الزهور",
        "المرزكة", "ياسمين الحمامات",
    ],
}

# ─────────────────────────────────────────────────────────────
# DÉPARTS
# ─────────────────────────────────────────────────────────────

DEPARTURES: dict[str, list[str]] = {
    "TN": ["beit", "dar", "bureau", "el-maktab", "hotel", "marsa", "ennasr", "funduk"],
    "FR": ["mon bureau", "mon hôtel", "la gare", "la marsa", "mon domicile", "carthage"],
    "EN": ["home", "office", "my office", "the hotel", "la marsa", "the station", "sfax"],
    "AR": ["المنزل", "المكتب", "الفندق", "المرسى", "المحطة", "قرطاج"],
}

# ─────────────────────────────────────────────────────────────
# DATES
# ─────────────────────────────────────────────────────────────

DATES: dict[str, list[str]] = {
    "TN": [
        "lyoum", "ghodwa", "el-jemaa", "el-khamis", "el-ahad",
        "el-itnin", "ba3d ghodwa", "tawwa", "el-talata", "el-arba3",
        "el-sebt", "nhar el-itnin el-jay", "nhar el-jemaa el-jay",
        "3 mai", "15 juin", "28 juillet", "2 aout",
        "10 septembre", "7 octobre", "22 novembre", "1 janvier",
    ],
    "FR": [
        "aujourd'hui", "demain", "vendredi", "lundi", "samedi",
        "après-demain", "ce soir", "mardi", "mercredi", "jeudi", "dimanche",
        "lundi prochain", "vendredi prochain", "dimanche prochain",
        "le 3 mai", "le 15 juin", "le 28 juillet", "le 2 août",
        "le 10 septembre", "le 7 octobre", "le 22 novembre", "le 31 décembre",
        "le 1er janvier", "le 14 février", "le 20 mars", "le 8 avril",
    ],
    "EN": [
        "today", "tomorrow", "friday", "monday", "saturday",
        "day after tomorrow", "tonight", "tuesday", "wednesday", "thursday", "sunday",
        "next monday", "next friday", "next saturday", "next sunday",
        "this friday", "this saturday", "this sunday", "this tuesday",
        "may 3rd", "june 15th", "july 28th", "august 2nd",
        "september 10th", "october 7th", "november 22nd", "december 31st",
        "january 1st", "february 14th", "march 20th", "april 8th",
    ],
    "AR": [
        "اليوم", "غدا", "الجمعة", "الاثنين", "السبت",
        "الخميس", "الأحد", "الأربعاء", "الثلاثاء",
        "الاثنين القادم", "الجمعة القادمة", "الأحد القادم",
        "3 ماي", "15 جوان", "28 جويلية", "2 أوت",
        "10 سبتمبر", "7 أكتوبر", "22 نوفمبر", "31 ديسمبر",
    ],
}

# ─────────────────────────────────────────────────────────────
# HEURES
# ─────────────────────────────────────────────────────────────

TIMES: dict[str, list[str]] = {
    "TN": [
        "sbeh", "3achiya", "dhuhr", "ba3d dhuhr", "leyl",
        "8h", "9h", "14h", "18h", "20h", "7h30", "8h30", "10h", "12h",
        "6h", "6h30", "7h", "9h30", "10h30", "11h", "11h30",
        "12h30", "13h", "13h30", "15h", "15h30", "16h", "16h30",
        "17h", "17h30", "19h", "19h30", "21h", "22h", "23h",
        "nouss el-lil",
    ],
    "FR": [
        "matin", "soir", "midi", "après-midi", "nuit", "minuit",
        "8h", "9h", "14h", "18h", "20h", "8h30", "14h30", "11h", "16h",
        "6h", "6h30", "7h", "7h30", "9h30", "10h", "10h30",
        "11h30", "12h30", "13h", "13h30", "15h", "15h30",
        "16h30", "17h", "17h30", "19h", "19h30", "21h", "22h", "23h",
    ],
    "EN": [
        "morning", "evening", "noon", "afternoon", "night", "midnight",
        "8h", "9h", "14h", "18h", "22h", "7h", "8h30", "13h", "15h",
        "6h", "6h30", "7h30", "9h30", "10h", "10h30", "11h",
        "11h30", "12h30", "13h30", "14h30", "15h30", "16h",
        "16h30", "17h", "17h30", "19h", "19h30", "20h", "21h", "23h",
    ],
    "AR": [
        "الصباح", "المساء", "الظهر", "الليل", "صباحا", "منتصف الليل",
        "8h", "9h", "14h", "18h", "20h",
        "6h", "6h30", "7h", "7h30", "8h30", "9h30", "10h", "10h30",
        "11h", "11h30", "12h30", "13h", "13h30", "14h30", "15h",
        "15h30", "16h", "16h30", "17h", "17h30", "19h", "19h30",
        "21h", "22h", "23h",
    ],
}

LANGUAGES: list[str] = list(DESTINATIONS.keys())