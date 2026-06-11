"""Test the exact failing scenario from dialog.py output."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.strict_normalization import (
    strict_normalize_location,
    strict_normalize_date,
    strict_normalize_time,
    strict_postprocess,
)

print("=== Scenario: 'JE VEUT allez a tunisa' ===\n")

# 1. Destination: "Tunisa" -> should fuzzy match to "Tunis"
loc = strict_normalize_location("Tunisa")
print(f"  'Tunisa' -> {loc!r}  (expect 'Tunis')")
assert loc == "Tunis", f"FAIL: got {loc!r}"

# 2. Date: "##eut" (BERT artifact) -> after stripping ## -> "eut" -> garbage -> None
#    _clean_bert_token strips "##" -> "eut"
#    strict_normalize_date("eut") -> None (garbage)
dt = strict_normalize_date("##eut")
print(f"  '##eut' -> {dt!r}  (expect None)")
assert dt is None, f"FAIL: got {dt!r}"

dt2 = strict_normalize_date("eut")
print(f"  'eut'   -> {dt2!r}  (expect None)")
assert dt2 is None, f"FAIL: got {dt2!r}"

# 3. Time: "2" -> should become "02:00"
tm = strict_normalize_time("2")
print(f"  '2'     -> {tm!r}  (expect '02:00')")
assert tm == "02:00", f"FAIL: got {tm!r}"

# 4. Full postprocess of the garbage scenario
raw = {"destination": "Tunisa", "departure": None, "date": "eut", "time": None}
result = strict_postprocess(raw, "JE VEUT allez a tunisa")
print(f"\n  Full postprocess:")
print(f"    destination = {result['destination']!r}  (expect 'Tunis')")
print(f"    departure   = {result['departure']!r}  (expect 'current_location')")
print(f"    date        = {result['date']!r}  (expect None)")
print(f"    time        = {result['time']!r}  (expect None)")
print(f"    missing     = {result['missing_fields']}")
assert result["destination"] == "Tunis"
assert result["departure"] == "current_location"
assert result["date"] is None
assert result["time"] is None
assert "date" in result["missing_fields"]
assert "time" in result["missing_fields"]

print("\n  ALL CHECKS PASSED!")
