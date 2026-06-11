"""
MOVIROO — tests/test_pipeline.py
Tests unitaires pour la normalisation et le dataset.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.normalization import (
    normalize_date, normalize_time, normalize_location, postprocess
)
from data.train_data import TRAIN_DATA, ann


# ─────────────────────────────────────────────────────────────
# normalize_date
# ─────────────────────────────────────────────────────────────

class TestNormalizeDate:
    today = date.today()

    def test_today_en(self):
        assert normalize_date("today") == self.today.isoformat()

    def test_today_fr(self):
        assert normalize_date("aujourd'hui") == self.today.isoformat()

    def test_today_tn(self):
        assert normalize_date("lyoum") == self.today.isoformat()

    def test_today_ar(self):
        assert normalize_date("اليوم") == self.today.isoformat()

    def test_tomorrow_en(self):
        expected = (self.today + timedelta(days=1)).isoformat()
        assert normalize_date("tomorrow") == expected

    def test_tomorrow_fr(self):
        expected = (self.today + timedelta(days=1)).isoformat()
        assert normalize_date("demain") == expected

    def test_tomorrow_tn(self):
        expected = (self.today + timedelta(days=1)).isoformat()
        assert normalize_date("ghodwa") == expected

    def test_day_after_tomorrow(self):
        expected = (self.today + timedelta(days=2)).isoformat()
        assert normalize_date("ba3d ghodwa") == expected
        assert normalize_date("après-demain") == expected
        assert normalize_date("day after tomorrow") == expected

    def test_none(self):
        assert normalize_date(None) is None

    def test_empty(self):
        assert normalize_date("") is None

    def test_date_slash(self):
        result = normalize_date("15/04")
        assert result is not None
        assert "04-15" in result

    def test_next_friday(self):
        result = normalize_date("next friday")
        assert result is not None
        from datetime import datetime
        d = datetime.fromisoformat(result)
        assert d.weekday() == 4  # vendredi


# ─────────────────────────────────────────────────────────────
# normalize_time
# ─────────────────────────────────────────────────────────────

class TestNormalizeTime:
    def test_h_format(self):
        assert normalize_time("18h") == "18:00"
        assert normalize_time("8h") == "08:00"
        assert normalize_time("8h30") == "08:30"

    def test_colon_format(self):
        assert normalize_time("14:00") == "14:00"
        assert normalize_time("09:30") == "09:30"

    def test_am_pm(self):
        assert normalize_time("9am") == "09:00"
        assert normalize_time("3pm") == "15:00"
        assert normalize_time("12am") == "00:00"
        assert normalize_time("12pm") == "12:00"

    def test_semantic_tn(self):
        assert normalize_time("sbeh")      == "morning"
        assert normalize_time("3achiya")   == "evening"
        assert normalize_time("ba3d dhuhr")== "afternoon"
        assert normalize_time("nouss el-lil") == "midnight"

    def test_semantic_fr(self):
        assert normalize_time("matin")     == "morning"
        assert normalize_time("soir")      == "evening"
        assert normalize_time("midi")      == "noon"
        assert normalize_time("après-midi")== "afternoon"

    def test_semantic_ar(self):
        assert normalize_time("الصباح")    == "morning"
        assert normalize_time("المساء")    == "evening"

    def test_none(self):
        assert normalize_time(None) is None


# ─────────────────────────────────────────────────────────────
# normalize_location
# ─────────────────────────────────────────────────────────────

class TestNormalizeLocation:
    def test_known_locations(self):
        assert normalize_location("hammamet") == "Hammamet"
        assert normalize_location("sfax")     == "Sfax"
        assert normalize_location("tnis")     == "Tunis"
        assert normalize_location("matar")    == "Airport"
        assert normalize_location("beit")     == "Home"
        assert normalize_location("bureau")   == "Office"
        assert normalize_location("gare")     == "Train Station"

    def test_arabic(self):
        assert normalize_location("سوسة")    == "Sousse"
        assert normalize_location("المطار")  == "Airport"
        assert normalize_location("المكتب")  == "Office"

    def test_unknown(self):
        result = normalize_location("unknown_place")
        assert result == "Unknown_Place"   # title-cased fallback

    def test_none(self):
        assert normalize_location(None) is None


# ─────────────────────────────────────────────────────────────
# postprocess
# ─────────────────────────────────────────────────────────────

class TestPostprocess:
    def test_full_fields(self):
        raw = {
            "destination": "hammamet",
            "departure":   "beit",
            "date":        "ghodwa",
            "time":        "18h",
        }
        result = postprocess(raw)
        assert result["destination"]    == "Hammamet"
        assert result["departure"]      == "Home"
        assert result["time"]           == "18:00"
        assert result["missing_fields"] == []

    def test_missing_destination(self):
        raw = {"date": "demain", "time": "matin"}
        result = postprocess(raw)
        assert "destination" in result["missing_fields"]

    def test_fallback_regex_time(self):
        raw = {}
        result = postprocess(raw, text="take me to tunis at 9h30")
        assert result["time"] == "09:30"   # fallback regex → normalized HH:MM

    def test_departure_default(self):
        raw = {"destination": "sfax", "date": "demain"}
        result = postprocess(raw)
        assert result["departure"] == "current_location"


# ─────────────────────────────────────────────────────────────
# Dataset integrity
# ─────────────────────────────────────────────────────────────

class TestDataset:
    def test_all_spans_valid(self):
        """Tous les spans doivent correspondre au texte."""
        errors = []
        for text, ann_dict in TRAIN_DATA:
            for start, end, label in ann_dict["entities"]:
                span = text[start:end]
                if not span.strip():
                    errors.append(f"Span vide [{start}:{end}] dans : {text[:50]}")
                if end > len(text):
                    errors.append(f"Span hors-limite [{start}:{end}] dans : {text[:50]}")
        assert errors == [], "\n".join(errors)

    def test_no_overlapping_spans(self):
        """Pas de chevauchement entre les spans d'un même exemple."""
        errors = []
        for text, ann_dict in TRAIN_DATA:
            entities = sorted(ann_dict["entities"])
            for i in range(len(entities) - 1):
                _, e1, _ = entities[i]
                s2, _, _ = entities[i + 1]
                if e1 > s2:
                    errors.append(f"Chevauchement dans : {text[:50]}")
        assert errors == [], "\n".join(errors)

    def test_valid_labels(self):
        """Seuls les labels autorisés sont utilisés."""
        allowed = {"DESTINATION", "DEPARTURE", "DATE", "TIME"}
        for text, ann_dict in TRAIN_DATA:
            for _, _, label in ann_dict["entities"]:
                assert label in allowed, f"Label inconnu '{label}' dans : {text[:50]}"

    def test_minimum_size(self):
        assert len(TRAIN_DATA) >= 100, f"Dataset trop petit : {len(TRAIN_DATA)} exemples"

    def test_all_languages_covered(self):
        """Au moins 10 exemples par langue (heuristique)."""
        tn = sum(1 for t, _ in TRAIN_DATA if any(w in t for w in ["ghodwa","nemchi","sbeh","3achiya"]))
        fr = sum(1 for t, _ in TRAIN_DATA if any(w in t for w in ["demain","matin","soir","aujourd"]))
        en = sum(1 for t, _ in TRAIN_DATA if any(w in t for w in ["tomorrow","morning","evening","tonight"]))
        ar = sum(1 for t, _ in TRAIN_DATA if any(w in t for w in ["غدا","اليوم","المطار","سوسة"]))
        assert tn >= 10, f"TN sous-représenté : {tn}"
        assert fr >= 10, f"FR sous-représenté : {fr}"
        assert en >= 10, f"EN sous-représenté : {en}"
        assert ar >= 10, f"AR sous-représenté : {ar}"


# ─────────────────────────────────────────────────────────────
# ann() helper
# ─────────────────────────────────────────────────────────────

class TestAnnHelper:
    def test_basic(self):
        text = "nheb nemchi hammamet ghodwa 18h"
        result = ann(text, ("hammamet", "DESTINATION"), ("ghodwa", "DATE"), ("18h", "TIME"))
        assert result[0] == text
        entities = result[1]["entities"]
        assert len(entities) == 3
        assert text[entities[0][0]:entities[0][1]] == "hammamet"

    def test_phrase_not_found(self):
        import pytest
        with pytest.raises(ValueError):
            ann("nheb nemchi sfax", ("tunis", "DESTINATION"))


# ─────────────────────────────────────────────────────────────
# knowledge.py — structure et cohérence
# ─────────────────────────────────────────────────────────────

class TestKnowledge:
    """Vérifie l'intégrité de config/knowledge.py."""

    def test_trigger_maps_not_empty(self):
        from config.knowledge import (
            DESTINATION_TRIGGER_MAP, DEPARTURE_TRIGGER_MAP,
            TIME_TRIGGER_MAP, DATE_TRIGGER_MAP,
        )
        assert len(DESTINATION_TRIGGER_MAP) >= 10
        assert len(DEPARTURE_TRIGGER_MAP)   >= 10
        assert len(TIME_TRIGGER_MAP)        >= 10
        assert len(DATE_TRIGGER_MAP)        >= 10

    def test_location_aliases_coverage(self):
        from config.knowledge import LOCATION_ALIASES
        # Lieux critiques présents
        for key in ["matar", "beit", "bureau", "gare", "hammamet", "sfax",
                    "المطار", "المنزل", "المكتب", "سوسة"]:
            assert key in LOCATION_ALIASES, f"'{key}' absent de LOCATION_ALIASES"

    def test_known_locations_not_empty(self):
        from config.knowledge import KNOWN_LOCATIONS
        assert len(KNOWN_LOCATIONS) >= 20

    def test_time_ranges_keys(self):
        from config.knowledge import TIME_RANGES
        for key in ["morning", "noon", "afternoon", "evening", "night", "midnight"]:
            assert key in TIME_RANGES, f"'{key}' absent de TIME_RANGES"

    def test_gold_examples_structure(self):
        from config.knowledge import GOLD_EXAMPLES
        assert len(GOLD_EXAMPLES) >= 10
        required_keys = {"input", "lang", "labels"}
        label_keys    = {"destination", "departure", "date", "time"}
        for ex in GOLD_EXAMPLES:
            assert required_keys <= ex.keys(), f"Clés manquantes dans : {ex}"
            assert label_keys    <= ex["labels"].keys()
            assert ex["lang"]    in ("TN", "FR", "EN", "AR")

    def test_lang_markers_all_languages(self):
        from config.knowledge import LANG_MARKERS
        for lang in ("TN", "FR", "EN", "AR"):
            assert lang in LANG_MARKERS
            assert len(LANG_MARKERS[lang]) >= 5, f"Trop peu de markers pour {lang}"

    def test_no_duplicate_keys_in_trigger_maps(self):
        """Vérifie qu'aucune liste de triggers n'a de doublons de 'word'."""
        from config.knowledge import (
            DESTINATION_TRIGGERS, DEPARTURE_TRIGGERS,
            TIME_TRIGGERS, DATE_TRIGGERS,
        )
        for name, lst in [
            ("DESTINATION", DESTINATION_TRIGGERS),
            ("DEPARTURE",   DEPARTURE_TRIGGERS),
            ("TIME",        TIME_TRIGGERS),
            ("DATE",        DATE_TRIGGERS),
        ]:
            words = [e["word"].lower() for e in lst]
            dups  = {w for w in words if words.count(w) > 1}
            assert not dups, f"Doublons dans {name}_TRIGGERS : {dups}"


# ─────────────────────────────────────────────────────────────
# Gold standard end-to-end
# ─────────────────────────────────────────────────────────────

class TestGoldStandard:
    """
    Vérifie que la normalisation produit les sorties attendues
    sur les exemples canoniques de config/knowledge.py.
    """

    def _run(self, example: dict) -> dict:
        from config.normalization import (
            normalize_date, normalize_time, normalize_location
        )
        labels = example["labels"]
        return {
            "destination": normalize_location(labels.get("destination")),
            "departure":   normalize_location(labels.get("departure")),
            "date":        normalize_date(labels.get("date")),
            "time":        normalize_time(labels.get("time")),
        }

    def test_tn_hammamet(self):
        from config.knowledge import GOLD_EXAMPLES
        ex = next(e for e in GOLD_EXAMPLES if "hammamet" in e["input"])
        r  = self._run(ex)
        assert r["destination"] == "Hammamet"
        assert r["departure"]   == "current_location"
        assert r["time"]        == "evening"

    def test_en_airport(self):
        from config.knowledge import GOLD_EXAMPLES
        ex = next(e for e in GOLD_EXAMPLES if "airport" in e["input"])
        r  = self._run(ex)
        assert r["destination"] == "Airport"
        assert r["time"]        == "22:00"

    def test_fr_marsa_centre(self):
        from config.knowledge import GOLD_EXAMPLES
        ex = next(e for e in GOLD_EXAMPLES if "marsa" in e["input"])
        r  = self._run(ex)
        assert r["destination"] == "City Center"
        assert r["departure"]   == "La Marsa"
        assert r["time"]        == "morning"

    def test_en_sfax_sousse(self):
        from config.knowledge import GOLD_EXAMPLES
        ex = next(e for e in GOLD_EXAMPLES if "sfax" in e["input"] and "sousse" in e["input"])
        r  = self._run(ex)
        assert r["destination"] == "Sousse"
        assert r["departure"]   == "Sfax"
        assert r["time"]        == "08:30"

    def test_tn_sfax_office(self):
        from config.knowledge import GOLD_EXAMPLES
        ex = next(e for e in GOLD_EXAMPLES if "el-maktab" in e["input"])
        r  = self._run(ex)
        assert r["destination"] == "Sfax"
        assert r["departure"]   == "Office"
        assert r["time"]        == "afternoon"

    def test_fr_bizerte_nabeul(self):
        from config.knowledge import GOLD_EXAMPLES
        ex = next(e for e in GOLD_EXAMPLES if "bizerte" in e["input"])
        r  = self._run(ex)
        assert r["destination"] == "Nabeul"
        assert r["departure"]   == "Bizerte"
        assert r["time"]        == "14:00"

    def test_all_gold_examples_parseable(self):
        """Tous les exemples doivent passer la normalisation sans erreur."""
        from config.knowledge import GOLD_EXAMPLES
        for ex in GOLD_EXAMPLES:
            r = self._run(ex)
            # destination et departure doivent toujours être non-None
            assert r["destination"] is not None or ex["labels"]["destination"] is None
            assert r["departure"]   is not None or ex["labels"]["departure"]   is None


# ─────────────────────────────────────────────────────────────
# detect_language — piloté par knowledge.LANG_MARKERS
# ─────────────────────────────────────────────────────────────

class TestDetectLanguage:
    def _detect(self, text):
        from scripts.dialog import detect_language
        return detect_language(text)

    def test_tn(self):
        assert self._detect("nheb nemchi hammamet ghodwa") == "TN"
        assert self._detect("bch nemchi sfax el-jemaa sbeh") == "TN"

    def test_fr(self):
        assert self._detect("je veux aller a tunis demain matin") == "FR"
        assert self._detect("taxi pour sousse vendredi soir") == "FR"

    def test_en(self):
        assert self._detect("take me to the airport tonight") == "EN"
        assert self._detect("I need a taxi to sousse tomorrow morning") == "EN"

    def test_ar(self):
        assert self._detect("أريد تاكسي إلى سوسة غدا") == "AR"
        assert self._detect("من هنا إلى المطار اليوم في المساء") == "AR"

    def test_unknown_fallback(self):
        # texte sans aucun marker → FR par défaut (latin)
        result = self._detect("xyz abc 123")
        assert result in ("TN", "FR", "EN", "AR")  # doit retourner quelque chose