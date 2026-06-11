"""
Tests for config/strict_normalization.py

Run:  python -m pytest test/test_strict_normalization.py -v
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.strict_normalization import (
    strict_normalize_location,
    strict_normalize_date,
    strict_normalize_time,
    strict_postprocess,
    strip_fillers,
)


# ─────────────────────────────────────────────────────────────
# LOCATION
# ─────────────────────────────────────────────────────────────

class TestLocation:

    def test_exact_alias(self):
        assert strict_normalize_location("hammamet") == "Hammamet"
        assert strict_normalize_location("touns") == "Tunis"
        assert strict_normalize_location("soussa") == "Sousse"
        assert strict_normalize_location("tnis") == "Tunis"

    def test_known_location_case(self):
        assert strict_normalize_location("Sfax") == "Sfax"
        assert strict_normalize_location("SFAX") == "Sfax"
        assert strict_normalize_location("djerba") == "Djerba"

    def test_fuzzy_fix_typo(self):
        # "tuinisa" is close to "tunis"
        result = strict_normalize_location("tuinisa")
        assert result is not None
        # "hamamett" close to "hammamet"
        result2 = strict_normalize_location("hamamett")
        assert result2 == "Hammamet"

    def test_reject_truncated(self):
        # "Tu" is too short (< 3 chars)
        assert strict_normalize_location("Tu") is None
        assert strict_normalize_location("s") is None

    def test_reject_garbage(self):
        assert strict_normalize_location("allrez") is None
        assert strict_normalize_location("xyzabc") is None

    def test_reject_numeric(self):
        assert strict_normalize_location("123") is None

    def test_none_input(self):
        assert strict_normalize_location(None) is None
        assert strict_normalize_location("") is None

    def test_arabic_alias(self):
        assert strict_normalize_location("تونس") == "Tunis"
        assert strict_normalize_location("سوسة") == "Sousse"

    def test_transport_locations(self):
        assert strict_normalize_location("airport") == "Airport"
        assert strict_normalize_location("matar") == "Airport"
        assert strict_normalize_location("gare") == "Train Station"


# ─────────────────────────────────────────────────────────────
# DATE
# ─────────────────────────────────────────────────────────────

class TestDate:

    def test_keywords(self):
        from datetime import date, timedelta
        today = date.today()
        assert strict_normalize_date("today") == today.isoformat()
        assert strict_normalize_date("tomorrow") == (today + timedelta(days=1)).isoformat()
        assert strict_normalize_date("demain") == (today + timedelta(days=1)).isoformat()
        assert strict_normalize_date("ghodwa") == (today + timedelta(days=1)).isoformat()

    def test_iso_passthrough(self):
        assert strict_normalize_date("2025-06-15") == "2025-06-15"

    def test_numeric_ddmm(self):
        result = strict_normalize_date("15/06")
        assert result is not None
        assert "06-15" in result

    def test_reject_garbage(self):
        assert strict_normalize_date("allrez") is None
        assert strict_normalize_date("ghodwaaa") is None  # not in keywords, but we added it
        assert strict_normalize_date("demn") is None
        assert strict_normalize_date("tunisia") is None

    def test_reject_time_as_date(self):
        # "8h" is a time token, not a date
        assert strict_normalize_date("8h") is None
        assert strict_normalize_date("8am") is None

    def test_none_input(self):
        assert strict_normalize_date(None) is None
        assert strict_normalize_date("") is None

    def test_weekdays_fr(self):
        result = strict_normalize_date("vendredi")
        assert result is not None  # should be a valid ISO date

    def test_dialectal_variants(self):
        from datetime import date, timedelta
        today = date.today()
        assert strict_normalize_date("ghodoa") == (today + timedelta(days=1)).isoformat()
        assert strict_normalize_date("lyoum") == today.isoformat()


# ─────────────────────────────────────────────────────────────
# TIME
# ─────────────────────────────────────────────────────────────

class TestTime:

    def test_hm_format(self):
        assert strict_normalize_time("8h") == "08:00"
        assert strict_normalize_time("18h30") == "18:30"
        assert strict_normalize_time("8h30") == "08:30"

    def test_colon_format(self):
        assert strict_normalize_time("08:00") == "08:00"
        assert strict_normalize_time("20:30") == "20:30"
        assert strict_normalize_time("14:00") == "14:00"

    def test_ampm_format(self):
        assert strict_normalize_time("8am") == "08:00"
        assert strict_normalize_time("10PM") == "22:00"
        assert strict_normalize_time("12am") == "00:00"
        assert strict_normalize_time("12pm") == "12:00"

    def test_bare_number(self):
        assert strict_normalize_time("8") == "08:00"
        assert strict_normalize_time("20") == "20:00"

    def test_semantic_keywords(self):
        assert strict_normalize_time("matin") == "morning"
        assert strict_normalize_time("soir") == "evening"
        assert strict_normalize_time("sbeh") == "morning"
        assert strict_normalize_time("3achiya") == "evening"

    def test_reject_garbage(self):
        assert strict_normalize_time("allrez") is None
        assert strict_normalize_time("tunisia") is None
        assert strict_normalize_time("demain") is None
        assert strict_normalize_time("hammamet") is None

    def test_none_input(self):
        assert strict_normalize_time(None) is None
        assert strict_normalize_time("") is None

    def test_out_of_range(self):
        assert strict_normalize_time("25h") is None
        assert strict_normalize_time("99:99") is None


# ─────────────────────────────────────────────────────────────
# FILLER STRIPPING
# ─────────────────────────────────────────────────────────────

class TestFillers:

    def test_strip_fr(self):
        assert "hammamet" in strip_fillers("je veux aller à hammamet").lower()
        assert "veux" not in strip_fillers("je veux aller à hammamet").lower()

    def test_strip_tn(self):
        cleaned = strip_fillers("nheb nemchi hammamet ghodwa")
        assert "hammamet" in cleaned.lower()

    def test_strip_en(self):
        cleaned = strip_fillers("I want to go to Sfax please")
        assert "sfax" in cleaned.lower()
        assert "please" not in cleaned.lower()


# ─────────────────────────────────────────────────────────────
# FULL POSTPROCESS
# ─────────────────────────────────────────────────────────────

class TestPostprocess:

    def test_full_valid(self):
        raw = {
            "destination": "hammamet",
            "departure": None,
            "date": "demain",
            "time": "8h",
        }
        result = strict_postprocess(raw)
        assert result["destination"] == "Hammamet"
        assert result["departure"] == "current_location"
        assert result["date"] is not None
        assert result["time"] == "08:00"
        assert result["missing_fields"] == []

    def test_garbage_rejected(self):
        raw = {
            "destination": "tuinisa",
            "departure": None,
            "date": "allrez",
            "time": "tunisia",
        }
        result = strict_postprocess(raw)
        assert result["date"] is None
        assert result["time"] is None
        assert "date" in result["missing_fields"]
        assert "time" in result["missing_fields"]

    def test_missing_fields_computed(self):
        raw = {"destination": None, "departure": None, "date": None, "time": None}
        result = strict_postprocess(raw)
        assert set(result["missing_fields"]) == {"destination", "date", "time"}
        assert result["departure"] == "current_location"

    def test_partial_entities(self):
        raw = {
            "destination": "sousse",
            "departure": None,
            "date": None,
            "time": "14h",
        }
        result = strict_postprocess(raw)
        assert result["destination"] == "Sousse"
        assert result["time"] == "14:00"
        assert "date" in result["missing_fields"]
        assert "destination" not in result["missing_fields"]
