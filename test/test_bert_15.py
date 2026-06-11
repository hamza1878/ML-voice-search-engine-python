"""Test what BERT predicts for '15' alone."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.dialog import NERModel

ner = NERModel('bert')
result = ner.predict('15')
print("BERT prediction for '15':", result)
