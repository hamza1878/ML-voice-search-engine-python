"""
MOVIROO — scripts/hybrid.py

Fusion intelligente BERT + spaCy :
  - BERT prioritaire (plus robuste sur les textes ambigus)
  - spaCy en fallback pour les champs non détectés
  - Si les deux détectent : on garde la valeur la plus longue

Usage:
    python scripts/hybrid.py
    python scripts/hybrid.py --text "nheb nemchi hammamet ghodwa 18h"
    python scripts/hybrid.py --bench          # benchmark sur le dataset de base
"""

import sys
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.strict_normalization import strict_postprocess

# ─────────────────────────────────────────────────────────────
# CHARGEMENT DES MODÈLES
# ─────────────────────────────────────────────────────────────

SPACY_MODEL_PATH = ROOT / "models" / "spacy"
BERT_MODEL_PATH  = ROOT / "models" / "bert"

FIELDS = ["destination", "departure", "date", "time"]


def _load_spacy():
    import spacy
    if not SPACY_MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle spaCy absent : {SPACY_MODEL_PATH}\n"
                                "  → python scripts/train_spacy.py --train")
    return spacy.load(SPACY_MODEL_PATH)


def _load_bert():
    try:
        from transformers import pipeline
    except ImportError:
        raise ImportError("pip install transformers torch")
    if not BERT_MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle BERT absent : {BERT_MODEL_PATH}\n"
                                "  → python scripts/train_bert.py --train")
    return pipeline(
        "token-classification",
        model=str(BERT_MODEL_PATH),
        aggregation_strategy="simple",
    )


# ─────────────────────────────────────────────────────────────
# PRÉDICTIONS INDIVIDUELLES
# ─────────────────────────────────────────────────────────────

def predict_spacy(nlp, text: str) -> dict[str, str | None]:
    """Extrait les entités brutes avec spaCy (sans normalisation)."""
    doc = nlp(text.lower())
    raw: dict[str, str | None] = {f: None for f in FIELDS}
    for ent in doc.ents:
        field = ent.label_.lower()
        if field in raw and raw[field] is None:
            raw[field] = ent.text
    return raw


def _clean_bert_token(word: str) -> str:
    """Strip BERT subword artifacts like '##eut' → '' (garbage)."""
    cleaned = word.strip()
    while cleaned.startswith("##"):
        cleaned = cleaned[2:]
    return cleaned.strip()


def predict_bert_raw(pipe, text: str) -> dict[str, str | None]:
    """Extrait les entités brutes avec BERT (sans normalisation)."""
    raw: dict[str, str | None] = {f: None for f in FIELDS}
    for ent in pipe(text):
        field = ent["entity_group"].lower()
        if field in raw and raw[field] is None:
            cleaned = _clean_bert_token(ent["word"])
            if cleaned:
                raw[field] = cleaned
    return raw


# ─────────────────────────────────────────────────────────────
# STRATÉGIE DE FUSION
# ─────────────────────────────────────────────────────────────

def _choose_best(val_bert: str | None, val_spacy: str | None) -> str | None:
    """
    Stratégie :
      1. BERT seul         → BERT
      2. spaCy seul        → spaCy
      3. Les deux présents → valeur la plus longue (souvent plus précise)
      4. Aucun             → None
    """
    if val_bert and val_spacy:
        return max(val_bert, val_spacy, key=len)
    return val_bert or val_spacy


# ─────────────────────────────────────────────────────────────
# PRÉDICTION HYBRIDE
# ─────────────────────────────────────────────────────────────

def hybrid_predict(text: str, nlp=None, pipe=None) -> dict:
    """
    Fusionne BERT et spaCy puis applique la normalisation.
    nlp  : modèle spaCy (chargé une fois à l'extérieur)
    pipe : pipeline BERT  (chargé une fois à l'extérieur)
    """
    text = text.lower().strip()

    bert_raw  = predict_bert_raw(pipe, text)  if pipe else {f: None for f in FIELDS}
    spacy_raw = predict_spacy(nlp, text)      if nlp  else {f: None for f in FIELDS}

    merged = {
        field: _choose_best(bert_raw.get(field), spacy_raw.get(field))
        for field in FIELDS
    }

    return strict_postprocess(merged, text)


# ─────────────────────────────────────────────────────────────
# BENCHMARK
# ─────────────────────────────────────────────────────────────

def benchmark(nlp, pipe) -> dict:
    """
    Évalue le modèle hybride sur le dataset de base.
    Retourne Précision / Rappel / F1.
    """
    from data.train_data import TRAIN_DATA
    from config.normalization import normalize_location, normalize_date, normalize_time

    NORMALIZERS = {
        "destination": normalize_location,
        "departure":   normalize_location,
        "date":        normalize_date,
        "time":        normalize_time,
    }

    tp = fp = fn = 0
    for text, ann in TRAIN_DATA:
        result = hybrid_predict(text, nlp=nlp, pipe=pipe)
        for s, e, label in ann["entities"]:
            field     = label.lower()
            true_val  = NORMALIZERS[field](text[s:e]) if field in NORMALIZERS else text[s:e]
            pred_val  = result.get(field)
            if pred_val and true_val and pred_val.lower() == true_val.lower():
                tp += 1
            elif pred_val:
                fp += 1
            else:
                fn += 1

    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    metrics = {"precision": round(p,3), "recall": round(r,3), "f1": round(f,3)}
    print(f"\n📊  Benchmark hybride → P={metrics['precision']}  R={metrics['recall']}  F1={metrics['f1']}")
    return metrics


# ─────────────────────────────────────────────────────────────
# DEMO SENTENCES
# ─────────────────────────────────────────────────────────────

DEMO_SENTENCES = [
    "taxi men sfax lel lac ghodwa 18h",
    "je veux aller a tunis demain matin",
    "take me to the airport tonight at 22h",
    "من هنا إلى سوسة غدا في المساء",
    "nheb nemchi hammamet ghodwa 18h",
    "reserver un taxi de la marsa vers le centre vendredi a 14h30",
    "I need a cab from home to the station friday at 8h",
]


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MOVIROO — NER Hybride BERT + spaCy")
    parser.add_argument("--text",  default=None, help="Analyser une phrase directement")
    parser.add_argument("--bench", action="store_true", help="Benchmark sur le dataset de base")
    parser.add_argument("--no-bert",  action="store_true", help="Utiliser seulement spaCy")
    parser.add_argument("--no-spacy", action="store_true", help="Utiliser seulement BERT")
    args = parser.parse_args()

    # Chargement des modèles
    print("📦  Chargement des modèles…")
    nlp  = None if args.no_spacy else _load_spacy()
    pipe = None if args.no_bert  else _load_bert()
    print("✅  Prêt.\n")

    # Benchmark
    if args.bench:
        benchmark(nlp, pipe)

    # Analyse directe
    if args.text:
        result = hybrid_predict(args.text, nlp=nlp, pipe=pipe)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Demo automatique
    print(f"{'─'*60}\n🧪  Démo\n{'─'*60}")
    for sentence in DEMO_SENTENCES:
        result = hybrid_predict(sentence, nlp=nlp, pipe=pipe)
        print(f"\n📝  {sentence}")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # Mode interactif
    print(f"\n{'─'*60}\n💬  Mode interactif (q pour quitter)\n{'─'*60}\n")
    while True:
        try:
            text = input("📝 > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text or text.lower() in ("q", "quit", "exit"):
            break
        result = hybrid_predict(text, nlp=nlp, pipe=pipe)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()


if __name__ == "__main__":
    main()