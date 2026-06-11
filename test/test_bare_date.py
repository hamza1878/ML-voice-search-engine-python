"""Test bare number dates."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.strict_normalization import strict_normalize_date

tests = [
    ("15", "should accept as day of current month"),
    ("5", "should accept as day of current month"),
    ("31", "should accept if valid day"),
    ("32", "should reject (invalid day)"),
    ("0", "should reject (invalid day)"),
]

for val, desc in tests:
    result = strict_normalize_date(val)
    status = "PASS" if (result is not None if val in ["15", "5", "31"] else result is None) else "FAIL"
    print(f"{status}: {val} -> {result!r} ({desc})")
