"""Test that ISO dates and times are extracted from full sentences."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.strict_normalization import strict_postprocess

# Scenario: "Taxi vers Tunis le 2026-05-18 à 07:00"
# BERT only extracts destination, misses date and time
raw = {"destination": "Tunis", "departure": None, "date": None, "time": None}
text = "Taxi vers Tunis le 2026-05-18 à 07:00"

result = strict_postprocess(raw, text)
print(f"Input: {text!r}")
print(f"  destination = {result['destination']!r}")
print(f"  departure   = {result['departure']!r}")
print(f"  date        = {result['date']!r}")
print(f"  time        = {result['time']!r}")
print(f"  missing     = {result['missing_fields']}")

assert result["destination"] == "Tunis", f"FAIL dest: {result['destination']}"
assert result["date"] == "2026-05-18", f"FAIL date: {result['date']}"
assert result["time"] == "07:00", f"FAIL time: {result['time']}"
assert result["missing_fields"] == [], f"FAIL missing: {result['missing_fields']}"

# Also test: "je veut aller demain a 14h30"
raw2 = {"destination": None, "departure": None, "date": None, "time": None}
text2 = "je veut aller demain a 14h30"
result2 = strict_postprocess(raw2, text2)
print(f"\nInput: {text2!r}")
print(f"  date = {result2['date']!r}")
print(f"  time = {result2['time']!r}")
assert result2["date"] is not None, f"FAIL date2: {result2['date']}"
assert result2["time"] == "14:30", f"FAIL time2: {result2['time']}"

print("\nALL PASSED!")
