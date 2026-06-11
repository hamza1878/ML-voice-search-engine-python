"""
MOVIROO — data/train_data.py

Dataset annoté manuellement, structuré par langue.
Couvre : TN / FR / EN / AR
         Tous les trigger words (destination, départ, date, heure)
         Tous les styles (ellipse, question, impératif, code-switching)
"""

# ─────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────

def ann(text: str, *entity_pairs: tuple[str, str]) -> tuple:
    """
    Crée un exemple annoté.

    Usage:
        ann("nheb nemchi sfax ghodwa 18h",
            ("sfax",   "DESTINATION"),
            ("ghodwa", "DATE"),
            ("18h",    "TIME"))
    """
    entities = []
    for phrase, label in entity_pairs:
        idx = text.find(phrase)
        if idx == -1:
            raise ValueError(f"'{phrase}' introuvable dans : '{text}'")
        entities.append((idx, idx + len(phrase), label))
    return (text, {"entities": entities})


# ─────────────────────────────────────────────────────────────
# SECTION 1 — TUNISIEN (TN)
# ─────────────────────────────────────────────────────────────

TRAIN_TN = [
    # ── Destination seule ────────────────────────────────────
    ann("taxi lel hammamet",
        ("hammamet", "DESTINATION")),
    ann("wein taxi lel matar",
        ("matar", "DESTINATION")),
    ann("khodni lel gare",
        ("gare", "DESTINATION")),
    ann("nemchi sousse tawwa",
        ("sousse", "DESTINATION")),

    # ── Destination + Date ───────────────────────────────────
    ann("nheb nemchi hammamet ghodwa",
        ("hammamet", "DESTINATION"), ("ghodwa", "DATE")),
    ann("taxi lel sfax el-jemaa",
        ("sfax", "DESTINATION"), ("el-jemaa", "DATE")),
    ann("lazem nemchi nabeul el-itnin",
        ("nabeul", "DESTINATION"), ("el-itnin", "DATE")),
    ann("bch nemchi sousse el-ahad",
        ("sousse", "DESTINATION"), ("el-ahad", "DATE")),
    ann("nemchi kairouan ba3d ghodwa",
        ("kairouan", "DESTINATION"), ("ba3d ghodwa", "DATE")),
    ann("taxi lel bizerte el-talata",
        ("bizerte", "DESTINATION"), ("el-talata", "DATE")),

    # ── Destination + Time ───────────────────────────────────
    ann("taxi lel tunis sbeh",
        ("tunis", "DESTINATION"), ("sbeh", "TIME")),
    ann("khodni sfax 3achiya",
        ("sfax", "DESTINATION"), ("3achiya", "TIME")),
    ann("nemchi matar 6h30",
        ("matar", "DESTINATION"), ("6h30", "TIME")),
    ann("khodni sfax el-jemaa leyl",
        ("sfax", "DESTINATION"), ("el-jemaa", "DATE"), ("leyl", "TIME")),

    # ── Destination + Date + Time ────────────────────────────
    ann("nheb nemchi hammamet ghodwa 18h",
        ("hammamet", "DESTINATION"), ("ghodwa", "DATE"), ("18h", "TIME")),
    ann("bch nemchi sfax el-jemaa fel sbeh",
        ("sfax", "DESTINATION"), ("el-jemaa", "DATE"), ("fel sbeh", "TIME")),
    ann("khodni lel matar tawwa",
        ("matar", "DESTINATION"), ("tawwa", "DATE")),
    ann("wein taxi lel sousse el-ahad 10h",
        ("sousse", "DESTINATION"), ("el-ahad", "DATE"), ("10h", "TIME")),
    ann("lazem nkoun fel matar el-jemaa 6h30",
        ("matar", "DESTINATION"), ("el-jemaa", "DATE"), ("6h30", "TIME")),
    ann("taxi lel bizerte el-arba3 3achiya",
        ("bizerte", "DESTINATION"), ("el-arba3", "DATE"), ("3achiya", "TIME")),
    ann("nemchi monastir el-sebt 9h30",
        ("monastir", "DESTINATION"), ("el-sebt", "DATE"), ("9h30", "TIME")),
    ann("khodni lel hospital tawwa",
        ("hospital", "DESTINATION"), ("tawwa", "DATE")),
    ann("nemchi kairouan ba3d ghodwa 11h",
        ("kairouan", "DESTINATION"), ("ba3d ghodwa", "DATE"), ("11h", "TIME")),
    ann("nheb nemchi djerba lyoum",
        ("djerba", "DESTINATION"), ("lyoum", "DATE")),
    ann("bch nemchi la marsa el-khamis dhuhr",
        ("la marsa", "DESTINATION"), ("el-khamis", "DATE"), ("dhuhr", "TIME")),
    ann("nemchi sfax el-talata nouss el-lil",
        ("sfax", "DESTINATION"), ("el-talata", "DATE"), ("nouss el-lil", "TIME")),
    ann("taxi lel itnin 8h30",
        ("itnin", "DATE"), ("8h30", "TIME")),

    # ── Départ + Destination (3–4 slots) ─────────────────────
    ann("taxi men sfax lel lac ghodwa 18h",
        ("sfax", "DEPARTURE"), ("lac", "DESTINATION"), ("ghodwa", "DATE"), ("18h", "TIME")),
    ann("nemchi sfax min el-maktab el-khamis ba3d dhuhr",
        ("sfax", "DESTINATION"), ("el-maktab", "DEPARTURE"), ("el-khamis", "DATE"), ("ba3d dhuhr", "TIME")),
    ann("taxi men ennasr lel lac lyoum 20h",
        ("ennasr", "DEPARTURE"), ("lac", "DESTINATION"), ("lyoum", "DATE"), ("20h", "TIME")),
    ann("3aybni taxi men beit lel tunis ghodwa sbeh",
        ("beit", "DEPARTURE"), ("tunis", "DESTINATION"), ("ghodwa", "DATE"), ("sbeh", "TIME")),
    ann("nemchi tunis men hotel el-talata 14h",
        ("tunis", "DESTINATION"), ("hotel", "DEPARTURE"), ("el-talata", "DATE"), ("14h", "TIME")),
    ann("khodni men dar lel matar ghodwa 7h",
        ("dar", "DEPARTURE"), ("matar", "DESTINATION"), ("ghodwa", "DATE"), ("7h", "TIME")),
    ann("3aybni taxi men bureau lel gare el-jemaa 16h",
        ("bureau", "DEPARTURE"), ("gare", "DESTINATION"), ("el-jemaa", "DATE"), ("16h", "TIME")),
    ann("men marsa lel tunis ghodwa fel sbeh",
        ("marsa", "DEPARTURE"), ("tunis", "DESTINATION"), ("ghodwa", "DATE"), ("fel sbeh", "TIME")),
    ann("khodni men beit lel ennasr lyoum 8h",
        ("beit", "DEPARTURE"), ("ennasr", "DESTINATION"), ("lyoum", "DATE"), ("8h", "TIME")),
    ann("men funduk lel carthage lyoum 15h",
        ("funduk", "DEPARTURE"), ("carthage", "DESTINATION"), ("lyoum", "DATE"), ("15h", "TIME")),
    ann("taxi men beit lel matar ghodwa 6h",
        ("beit", "DEPARTURE"), ("matar", "DESTINATION"), ("ghodwa", "DATE"), ("6h", "TIME")),
    ann("khodni men el-maktab lel lac el-arba3 18h",
        ("el-maktab", "DEPARTURE"), ("lac", "DESTINATION"), ("el-arba3", "DATE"), ("18h", "TIME")),
    ann("nheb nemchi il touns men hammamet ghodwa 18h",
        ("touns", "DESTINATION"), ("hammamet", "DEPARTURE"), ("ghodwa", "DATE"), ("18h", "TIME")),

    # ── Style ellipse ────────────────────────────────────────
    ann("sfax el-jemaa sbeh",
        ("sfax", "DESTINATION"), ("el-jemaa", "DATE"), ("sbeh", "TIME")),
    ann("tunis ghodwa 18h",
        ("tunis", "DESTINATION"), ("ghodwa", "DATE"), ("18h", "TIME")),
    ann("matar tawwa",
        ("matar", "DESTINATION"), ("tawwa", "DATE")),
    ann("hammamet el-sebt 9h",
        ("hammamet", "DESTINATION"), ("el-sebt", "DATE"), ("9h", "TIME")),
]

# ─────────────────────────────────────────────────────────────
# SECTION 2 — FRANÇAIS (FR)
# ─────────────────────────────────────────────────────────────

TRAIN_FR = [
    # ── Destination seule ────────────────────────────────────
    ann("taxi pour sfax",
        ("sfax", "DESTINATION")),
    ann("direction kairouan",
        ("kairouan", "DESTINATION")),
    ann("emmene moi a l aeroport",
        ("l aeroport", "DESTINATION")),

    # ── Destination + Date ───────────────────────────────────
    ann("je veux aller a tunis demain",
        ("tunis", "DESTINATION"), ("demain", "DATE")),
    ann("taxi pour djerba apres-demain",
        ("djerba", "DESTINATION"), ("apres-demain", "DATE")),
    ann("direction sousse samedi",
        ("sousse", "DESTINATION"), ("samedi", "DATE")),
    ann("aller a sfax lundi prochain",
        ("sfax", "DESTINATION"), ("lundi prochain", "DATE")),
    ann("rendez vous a monastir dimanche prochain",
        ("monastir", "DESTINATION"), ("dimanche prochain", "DATE")),

    # ── Destination + Time ───────────────────────────────────
    ann("taxi vers nabeul a 10h",
        ("nabeul", "DESTINATION"), ("10h", "TIME")),
    ann("je dois etre a l aeroport pour 6h",
        ("l aeroport", "DESTINATION"), ("6h", "TIME")),

    # ── Destination + Date + Time ────────────────────────────
    ann("je veux aller a tunis demain matin",
        ("tunis", "DESTINATION"), ("demain", "DATE"), ("matin", "TIME")),
    ann("emmene moi a l aeroport ce soir a 22h",
        ("l aeroport", "DESTINATION"), ("ce soir", "DATE"), ("22h", "TIME")),
    ann("je dois arriver a sousse lundi a 8h",
        ("sousse", "DESTINATION"), ("lundi", "DATE"), ("8h", "TIME")),
    ann("taxi pour nabeul apres-demain a 10h",
        ("nabeul", "DESTINATION"), ("apres-demain", "DATE"), ("10h", "TIME")),
    ann("taxi pour djerba aujourd hui soir",
        ("djerba", "DESTINATION"), ("aujourd hui", "DATE"), ("soir", "TIME")),
    ann("je veux aller a hammamet samedi apres-midi",
        ("hammamet", "DESTINATION"), ("samedi", "DATE"), ("apres-midi", "TIME")),
    ann("direction kairouan ce soir",
        ("kairouan", "DESTINATION"), ("ce soir", "DATE")),
    ann("taxi pour le lac ce soir a 20h",
        ("le lac", "DESTINATION"), ("ce soir", "DATE"), ("20h", "TIME")),
    ann("je dois etre a la gare lundi a 6h30",
        ("la gare", "DESTINATION"), ("lundi", "DATE"), ("6h30", "TIME")),
    ann("emmene moi a kairouan mardi a 13h",
        ("kairouan", "DESTINATION"), ("mardi", "DATE"), ("13h", "TIME")),
    ann("direction sousse samedi matin",
        ("sousse", "DESTINATION"), ("samedi", "DATE"), ("matin", "TIME")),
    ann("taxi pour hammamet vendredi soir",
        ("hammamet", "DESTINATION"), ("vendredi", "DATE"), ("soir", "TIME")),
    ann("je veux aller a bizerte demain nuit",
        ("bizerte", "DESTINATION"), ("demain", "DATE"), ("nuit", "TIME")),
    ann("aller a tunis vendredi a minuit",
        ("tunis", "DESTINATION"), ("vendredi", "DATE"), ("minuit", "TIME")),

    # ── Départ + Destination (3–4 slots) ─────────────────────
    ann("taxi depuis bizerte vers sfax samedi a 9h",
        ("bizerte", "DEPARTURE"), ("sfax", "DESTINATION"), ("samedi", "DATE"), ("9h", "TIME")),
    ann("reserver un taxi de la marsa vers le centre vendredi a 14h30",
        ("la marsa", "DEPARTURE"), ("le centre", "DESTINATION"), ("vendredi", "DATE"), ("14h30", "TIME")),
    ann("je pars de mon bureau pour monastir jeudi a 15h",
        ("mon bureau", "DEPARTURE"), ("monastir", "DESTINATION"), ("jeudi", "DATE"), ("15h", "TIME")),
    ann("de bizerte a nabeul mercredi a 14h00",
        ("bizerte", "DEPARTURE"), ("nabeul", "DESTINATION"), ("mercredi", "DATE"), ("14h00", "TIME")),
    ann("j ai besoin d un taxi de carthage a tunis lundi matin",
        ("carthage", "DEPARTURE"), ("tunis", "DESTINATION"), ("lundi", "DATE"), ("matin", "TIME")),
    ann("aller a sfax depuis la gare vendredi a 7h",
        ("la gare", "DEPARTURE"), ("sfax", "DESTINATION"), ("vendredi", "DATE"), ("7h", "TIME")),
    ann("un taxi de mon hotel au centre ville demain a 9h30",
        ("mon hotel", "DEPARTURE"), ("centre ville", "DESTINATION"), ("demain", "DATE"), ("9h30", "TIME")),
    ann("conduire de bizerte a tunis dimanche a 11h",
        ("bizerte", "DEPARTURE"), ("tunis", "DESTINATION"), ("dimanche", "DATE"), ("11h", "TIME")),
    ann("reserver un taxi demain matin de la marsa vers le centre",
        ("la marsa", "DEPARTURE"), ("le centre", "DESTINATION"), ("demain", "DATE"), ("matin", "TIME")),
    ann("taxi depuis mon bureau vers l aeroport aujourd hui a 18h",
        ("mon bureau", "DEPARTURE"), ("l aeroport", "DESTINATION"), ("aujourd hui", "DATE"), ("18h", "TIME")),
    ann("un taxi de mon domicile a l aeroport demain a 5h",
        ("mon domicile", "DEPARTURE"), ("l aeroport", "DESTINATION"), ("demain", "DATE"), ("5h", "TIME")),
    ann("de carthage a monastir mercredi a 10h",
        ("carthage", "DEPARTURE"), ("monastir", "DESTINATION"), ("mercredi", "DATE"), ("10h", "TIME")),
    ann("aller de la marsa a sfax vendredi a midi",
        ("la marsa", "DEPARTURE"), ("sfax", "DESTINATION"), ("vendredi", "DATE"), ("midi", "TIME")),
    ann("taxi de mon bureau vers sfax vendredi a 14h",
        ("mon bureau", "DEPARTURE"), ("sfax", "DESTINATION"), ("vendredi", "DATE"), ("14h", "TIME")),
    ann("je pars de la gare pour sousse demain a 9h",
        ("la gare", "DEPARTURE"), ("sousse", "DESTINATION"), ("demain", "DATE"), ("9h", "TIME")),

    # ── Style ellipse ────────────────────────────────────────
    ann("sousse demain matin",
        ("sousse", "DESTINATION"), ("demain", "DATE"), ("matin", "TIME")),
    ann("hammamet vendredi 18h",
        ("hammamet", "DESTINATION"), ("vendredi", "DATE"), ("18h", "TIME")),
    ann("sfax samedi 9h",
        ("sfax", "DESTINATION"), ("samedi", "DATE"), ("9h", "TIME")),

    # ── Numeric dates (day + month) ─────────────────────────
    ann("taxi pour tunis le 15 juin",
        ("tunis", "DESTINATION"), ("le 15 juin", "DATE")),
    ann("je veux aller a hammamet le 1er juillet a 18h",
        ("hammamet", "DESTINATION"), ("le 1er juillet", "DATE"), ("18h", "TIME")),
    ann("aller a sfax le 12 aout",
        ("sfax", "DESTINATION"), ("le 12 aout", "DATE")),
    ann("taxi pour sousse le 3 septembre a 10h",
        ("sousse", "DESTINATION"), ("le 3 septembre", "DATE"), ("10h", "TIME")),
    ann("direction monastir le 20 decembre",
        ("monastir", "DESTINATION"), ("le 20 decembre", "DATE")),
    ann("nheb nemchi tunis 15 juan",
        ("tunis", "DESTINATION"), ("15 juan", "DATE")),
    ann("nemchi hammamet 12 juillet",
        ("hammamet", "DESTINATION"), ("12 juillet", "DATE")),
    ann("taxi lel sfax le 8 mai",
        ("sfax", "DESTINATION"), ("le 8 mai", "DATE")),

    # ── Numeric dates (DD/MM format) ───────────────────────
    ann("taxi pour tunis 15/06",
        ("tunis", "DESTINATION"), ("15/06", "DATE")),
    ann("aller a hammamet 12/07 a 18h",
        ("hammamet", "DESTINATION"), ("12/07", "DATE"), ("18h", "TIME")),
    ann("je veux aller a sfax 03-08",
        ("sfax", "DESTINATION"), ("03-08", "DATE")),
]

TRAIN_EN = [
    # ── Destination seule ────────────────────────────────────
    ann("taxi to hammamet",
        ("hammamet", "DESTINATION")),
    ann("I need a ride to the airport",
        ("the airport", "DESTINATION")),
    ann("take me to sousse",
        ("sousse", "DESTINATION")),

    # ── Destination + Date ───────────────────────────────────
    ann("going to sfax tomorrow",
        ("sfax", "DESTINATION"), ("tomorrow", "DATE")),
    ann("I need a taxi to nabeul saturday",
        ("nabeul", "DESTINATION"), ("saturday", "DATE")),
    ann("taxi to sousse day after tomorrow",
        ("sousse", "DESTINATION"), ("day after tomorrow", "DATE")),
    ann("book a taxi to kairouan next friday",
        ("kairouan", "DESTINATION"), ("next friday", "DATE")),
    ann("going to nabeul this saturday",
        ("nabeul", "DESTINATION"), ("this saturday", "DATE")),

    # ── Destination + Time ───────────────────────────────────
    ann("take me to the airport at 6h",
        ("the airport", "DESTINATION"), ("6h", "TIME")),
    ann("I need a ride to monastir at noon",
        ("monastir", "DESTINATION"), ("noon", "TIME")),

    # ── Destination + Date + Time ────────────────────────────
    ann("take me to the airport tonight at 22h",
        ("the airport", "DESTINATION"), ("tonight", "DATE"), ("22h", "TIME")),
    ann("book a ride to monastir next monday at 7h",
        ("monastir", "DESTINATION"), ("next monday", "DATE"), ("7h", "TIME")),
    ann("get me a taxi to hammamet friday at 18h",
        ("hammamet", "DESTINATION"), ("friday", "DATE"), ("18h", "TIME")),
    ann("I want to go to djerba saturday at 10h",
        ("djerba", "DESTINATION"), ("saturday", "DATE"), ("10h", "TIME")),
    ann("taxi to nabeul day after tomorrow at 11h",
        ("nabeul", "DESTINATION"), ("day after tomorrow", "DATE"), ("11h", "TIME")),
    ann("I have to reach the train station tomorrow at 6h",
        ("the train station", "DESTINATION"), ("tomorrow", "DATE"), ("6h", "TIME")),
    ann("going to tunis today evening",
        ("tunis", "DESTINATION"), ("today", "DATE"), ("evening", "TIME")),
    ann("book a taxi to kairouan next friday at 7h30",
        ("kairouan", "DESTINATION"), ("next friday", "DATE"), ("7h30", "TIME")),
    ann("I need a taxi to la marsa tonight at 21h",
        ("la marsa", "DESTINATION"), ("tonight", "DATE"), ("21h", "TIME")),
    ann("heading to monastir tomorrow at noon",
        ("monastir", "DESTINATION"), ("tomorrow", "DATE"), ("noon", "TIME")),
    ann("I want a taxi to sfax this tuesday at 10h",
        ("sfax", "DESTINATION"), ("this tuesday", "DATE"), ("10h", "TIME")),
    ann("taxi to carthage tomorrow night",
        ("carthage", "DESTINATION"), ("tomorrow", "DATE"), ("night", "TIME")),

    # ── Départ + Destination (3–4 slots) ─────────────────────
    ann("I need a taxi from sfax to sousse tomorrow at 8h30",
        ("sfax", "DEPARTURE"), ("sousse", "DESTINATION"), ("tomorrow", "DATE"), ("8h30", "TIME")),
    ann("I need a ride from home to the airport tomorrow morning",
        ("home", "DEPARTURE"), ("the airport", "DESTINATION"), ("tomorrow", "DATE"), ("morning", "TIME")),
    ann("ride from la marsa to downtown today at noon",
        ("la marsa", "DEPARTURE"), ("downtown", "DESTINATION"), ("today", "DATE"), ("noon", "TIME")),
    ann("take me to sousse from my office thursday afternoon",
        ("my office", "DEPARTURE"), ("sousse", "DESTINATION"), ("thursday", "DATE"), ("afternoon", "TIME")),
    ann("pick me up at the hotel and take me to sfax sunday at 8h",
        ("the hotel", "DEPARTURE"), ("sfax", "DESTINATION"), ("sunday", "DATE"), ("8h", "TIME")),
    ann("can you take me from carthage to bizerte friday at 9h",
        ("carthage", "DEPARTURE"), ("bizerte", "DESTINATION"), ("friday", "DATE"), ("9h", "TIME")),
    ann("need a cab from the station to hammamet this saturday at 14h",
        ("the station", "DEPARTURE"), ("hammamet", "DESTINATION"), ("this saturday", "DATE"), ("14h", "TIME")),
    ann("take me from home to the airport tomorrow at 5h30",
        ("home", "DEPARTURE"), ("the airport", "DESTINATION"), ("tomorrow", "DATE"), ("5h30", "TIME")),
    ann("drop me at sousse from sfax wednesday at 15h",
        ("sfax", "DEPARTURE"), ("sousse", "DESTINATION"), ("wednesday", "DATE"), ("15h", "TIME")),
    ann("from the hotel to the airport sunday at 6h",
        ("the hotel", "DEPARTURE"), ("the airport", "DESTINATION"), ("sunday", "DATE"), ("6h", "TIME")),
    ann("take me to djerba from tunis next thursday morning",
        ("tunis", "DEPARTURE"), ("djerba", "DESTINATION"), ("next thursday", "DATE"), ("morning", "TIME")),
    ann("going to the airport from my office today at 17h",
        ("my office", "DEPARTURE"), ("the airport", "DESTINATION"), ("today", "DATE"), ("17h", "TIME")),
    ann("can I get a cab from home to the station friday at 8h",
        ("home", "DEPARTURE"), ("the station", "DESTINATION"), ("friday", "DATE"), ("8h", "TIME")),
    ann("ride from sfax to hammamet saturday at 8h",
        ("sfax", "DEPARTURE"), ("hammamet", "DESTINATION"), ("saturday", "DATE"), ("8h", "TIME")),

    # ── Code-switching + Ellipse ─────────────────────────────
    ann("hammamet tomorrow 9h",
        ("hammamet", "DESTINATION"), ("tomorrow", "DATE"), ("9h", "TIME")),
    ann("sfax friday morning",
        ("sfax", "DESTINATION"), ("friday", "DATE"), ("morning", "TIME")),
    ann("taxi from beit to sousse demain morning",
        ("beit", "DEPARTURE"), ("sousse", "DESTINATION"), ("demain", "DATE"), ("morning", "TIME")),
]

# ─────────────────────────────────────────────────────────────
# SECTION 4 — ARABE (AR)
# ─────────────────────────────────────────────────────────────

TRAIN_AR = [
    # ── Destination seule ────────────────────────────────────
    ann("تاكسي إلى سوسة",
        ("سوسة", "DESTINATION")),
    ann("خذني إلى المطار",
        ("المطار", "DESTINATION")),

    # ── Destination + Date ───────────────────────────────────
    ann("أريد الذهاب إلى تونس اليوم",
        ("تونس", "DESTINATION"), ("اليوم", "DATE")),
    ann("تاكسي إلى بنزرت الجمعة",
        ("بنزرت", "DESTINATION"), ("الجمعة", "DATE")),
    ann("أريد الذهاب إلى القيروان الاثنين القادم",
        ("القيروان", "DESTINATION"), ("الاثنين القادم", "DATE")),

    # ── Destination + Date + Time ────────────────────────────
    ann("من هنا إلى سوسة غدا في المساء",
        ("سوسة", "DESTINATION"), ("غدا", "DATE"), ("المساء", "TIME")),
    ann("أريد الذهاب إلى سوسة غدا في المساء",
        ("سوسة", "DESTINATION"), ("غدا", "DATE"), ("المساء", "TIME")),
    ann("خذني إلى المطار اليوم الساعة 20h",
        ("المطار", "DESTINATION"), ("اليوم", "DATE"), ("20h", "TIME")),
    ann("تاكسي نحو صفاقس يوم الجمعة صباحا",
        ("صفاقس", "DESTINATION"), ("الجمعة", "DATE"), ("صباحا", "TIME")),
    ann("تاكسي إلى بنزرت يوم الأربعاء في المساء",
        ("بنزرت", "DESTINATION"), ("الأربعاء", "DATE"), ("المساء", "TIME")),
    ann("أريد تاكسي إلى حمام الأنف غدا في 18h",
        ("حمام الأنف", "DESTINATION"), ("غدا", "DATE"), ("18h", "TIME")),
    ann("أحتاج تاكسي إلى المطار اليوم الساعة 6h",
        ("المطار", "DESTINATION"), ("اليوم", "DATE"), ("6h", "TIME")),
    ann("مطار غدا 6h",
        ("مطار", "DESTINATION"), ("غدا", "DATE"), ("6h", "TIME")),

    # ── Départ + Destination (3–4 slots) ─────────────────────
    ann("احتاج تاكسي من المكتب إلى المطار غدا الساعة 7h",
        ("المكتب", "DEPARTURE"), ("المطار", "DESTINATION"), ("غدا", "DATE"), ("7h", "TIME")),
    ann("من المنزل إلى سوسة الجمعة صباحا",
        ("المنزل", "DEPARTURE"), ("سوسة", "DESTINATION"), ("الجمعة", "DATE"), ("صباحا", "TIME")),
    ann("انطلاق من الفندق وصول المطار غدا في 6h",
        ("الفندق", "DEPARTURE"), ("المطار", "DESTINATION"), ("غدا", "DATE"), ("6h", "TIME")),
    ann("احتاج تاكسي من المرسى إلى وسط المدينة الاثنين صباحا",
        ("المرسى", "DEPARTURE"), ("وسط المدينة", "DESTINATION"), ("الاثنين", "DATE"), ("صباحا", "TIME")),
    ann("من المطار إلى الفندق اليوم في المساء",
        ("المطار", "DEPARTURE"), ("الفندق", "DESTINATION"), ("اليوم", "DATE"), ("المساء", "TIME")),
    ann("أريد تاكسي من المكتب إلى قرطاج الثلاثاء في المساء",
        ("المكتب", "DEPARTURE"), ("قرطاج", "DESTINATION"), ("الثلاثاء", "DATE"), ("المساء", "TIME")),
    ann("أريد تاكسي إلى تونس 15 جوان",
        ("تونس", "DESTINATION"), ("15 جوان", "DATE")),
    ann("خذني إلى المطار 12 جويلية",
        ("المطار", "DESTINATION"), ("12 جويلية", "DATE")),
    ann("تاكسي إلى سوسة 3 أوت",
        ("سوسة", "DESTINATION"), ("3 أوت", "DATE")),
    ann("أريد الذهاب إلى الحمامات 1 جانفي",
        ("الحمامات", "DESTINATION"), ("1 جانفي", "DATE")),
    ann("من المنزل إلى صفاقس 15/06",
        ("المنزل", "DEPARTURE"), ("صفاقس", "DESTINATION"), ("15/06", "DATE")),
]

# ─────────────────────────────────────────────────────────────
# DATASET FINAL
# ─────────────────────────────────────────────────────────────

TRAIN_DATA: list[tuple] = TRAIN_TN + TRAIN_FR + TRAIN_EN + TRAIN_AR