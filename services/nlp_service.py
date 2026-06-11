"""
MOVIROO — backend/services/nlp_service.py

Thin wrapper around the existing hybrid_predict() function.
No NLP logic is duplicated here — we only import and call.
"""

import sys
from pathlib import Path

# ── Point to the project root so existing imports still work ──
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent          # adjust if needed
sys.path.insert(0, str(PROJECT_ROOT))

# ─────────────────────────────────────────────────────────────
# LAZY MODEL LOADING  (models loaded once, reused across requests)
# ─────────────────────────────────────────────────────────────

class NLPService:
    """
    Wraps hybrid_predict() with lazy model loading.
    Models are loaded once on first call to avoid startup latency.
    """

    def __init__(self):
        self._nlp   = None   # spaCy model
        self._pipe  = None   # BERT pipeline
        self._ready = False
        self.model_name = "hybrid (spaCy + BERT)"

    # ── Internal loaders ──────────────────────────────────────

    def _ensure_loaded(self):
        if self._ready:
            return
        try:
            from scripts.hybrid import _load_spacy, _load_bert
            print("📦  Loading spaCy model…")
            self._nlp  = _load_spacy()
            print("📦  Loading BERT model…")
            self._pipe = _load_bert()
            print("✅  NLP models ready.")
        except Exception as e:
            print(f"⚠  Could not load full hybrid models: {e}")
            print("   Falling back to spaCy-only mode.")
            try:
                from scripts.hybrid import _load_spacy
                self._nlp = _load_spacy()
                self.model_name = "spaCy only"
            except Exception as e2:
                print(f"⚠  spaCy also unavailable: {e2}")
                self.model_name = "stub (no model)"
        self._ready = True

    # ── Public API ────────────────────────────────────────────

    def predict(self, text: str) -> dict:
        """
        Run NER + postprocessing on text.
        Returns:
            {
                "destination": str | None,
                "departure":   str | None,
                "date":        str | None,
                "time":        str | None,
                "missing_fields": list[str],
            }
        """
        self._ensure_loaded()

        # Try full hybrid
        if self._nlp or self._pipe:
            try:
                from scripts.hybrid import hybrid_predict
                return hybrid_predict(text, nlp=self._nlp, pipe=self._pipe)
            except Exception as e:
                print(f"⚠  hybrid_predict error: {e}")

        # Ultimate fallback: empty result
        return {
            "destination": None,
            "departure":   None,
            "date":        None,
            "time":        None,
            "missing_fields": ["destination", "date", "time"],
        }