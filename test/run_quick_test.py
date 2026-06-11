"""Quick smoke test for strict normalization."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.strict_normalization import (
    strict_normalize_location,
    strict_normalize_date,
    strict_normalize_time,
    strict_postprocess,
    strip_fillers,
)

passed = 0
failed = 0

def check(label, actual, expected):
    global passed, failed
    ok = actual == expected
    status = "PASS" if ok else "FAIL"
    if not ok:
        failed += 1
        print(f"  {status}: {label} => got {actual!r}, expected {expected!r}")
    else:
        passed += 1
        print(f"  {status}: {label}")

print("=== LOCATION ===")
check("hammamet",   strict_normalize_location("hammamet"),   "Hammamet")
check("touns",      strict_normalize_location("touns"),      "Tunis")
check("tnis",       strict_normalize_location("tnis"),       "Tunis")
check("soussa",     strict_normalize_location("soussa"),     "Sousse")
check("airport",    strict_normalize_location("airport"),    "Airport")
check("matar",      strict_normalize_location("matar"),      "Airport")
check("Tu reject",  strict_normalize_location("Tu"),         None)
check("s reject",   strict_normalize_location("s"),          None)
check("xyzabc",     strict_normalize_location("xyzabc"),     None)
check("None",       strict_normalize_location(None),         None)
check("empty",      strict_normalize_location(""),           None)
check("arabic",     strict_normalize_location("تونس"),       "Tunis")
check("hamamett",   strict_normalize_location("hamamett"),   "Hammamet")

print("\n=== DATE ===")
from datetime import date, timedelta
today = date.today()
tmr = (today + timedelta(days=1)).isoformat()
check("today",      strict_normalize_date("today"),      today.isoformat())
check("tomorrow",   strict_normalize_date("tomorrow"),   tmr)
check("demain",     strict_normalize_date("demain"),     tmr)
check("ghodwa",     strict_normalize_date("ghodwa"),     tmr)
check("ghodoa",     strict_normalize_date("ghodoa"),     tmr)
check("lyoum",      strict_normalize_date("lyoum"),      today.isoformat())
check("ISO",        strict_normalize_date("2025-06-15"), "2025-06-15")
check("allrez",     strict_normalize_date("allrez"),     None)
check("demn",       strict_normalize_date("demn"),       None)
check("tunisia",    strict_normalize_date("tunisia"),    None)
check("8h reject",  strict_normalize_date("8h"),         None)
check("8am reject", strict_normalize_date("8am"),        None)
check("None",       strict_normalize_date(None),         None)

print("\n=== TIME ===")
check("8h",        strict_normalize_time("8h"),      "08:00")
check("18h30",     strict_normalize_time("18h30"),   "18:30")
check("08:00",     strict_normalize_time("08:00"),   "08:00")
check("20:30",     strict_normalize_time("20:30"),   "20:30")
check("8am",       strict_normalize_time("8am"),     "08:00")
check("10PM",      strict_normalize_time("10PM"),    "22:00")
check("bare 8",    strict_normalize_time("8"),       "08:00")
check("matin",     strict_normalize_time("matin"),   "morning")
check("soir",      strict_normalize_time("soir"),    "evening")
check("allrez",    strict_normalize_time("allrez"),  None)
check("tunisia",   strict_normalize_time("tunisia"), None)
check("demain",    strict_normalize_time("demain"),  None)
check("None",      strict_normalize_time(None),      None)
check("25h OOR",   strict_normalize_time("25h"),     None)

print("\n=== FILLERS ===")
c1 = strip_fillers("je veux aller à hammamet")
check("FR fillers", "veux" not in c1.lower() and "hammamet" in c1.lower(), True)
c2 = strip_fillers("I want to go to Sfax please")
check("EN fillers", "please" not in c2.lower() and "sfax" in c2.lower(), True)

print("\n=== POSTPROCESS ===")
r1 = strict_postprocess({"destination": "hammamet", "departure": None, "date": "demain", "time": "8h"})
check("full valid dest",    r1["destination"], "Hammamet")
check("full valid dep",     r1["departure"],   "current_location")
check("full valid time",    r1["time"],        "08:00")
check("full valid missing", r1["missing_fields"], [])

r2 = strict_postprocess({"destination": None, "departure": None, "date": "allrez", "time": "tunisia"})
check("garbage date",    r2["date"], None)
check("garbage time",    r2["time"], None)
check("garbage missing", "date" in r2["missing_fields"] and "time" in r2["missing_fields"], True)

print(f"\n{'='*40}")
print(f"PASSED: {passed}  |  FAILED: {failed}")
if failed == 0:
    print("ALL TESTS PASSED!")
else:
    print(f"{failed} test(s) FAILED")
