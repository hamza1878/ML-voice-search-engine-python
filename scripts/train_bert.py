"""
MOVIROO — scripts/train_bert.py

Fine-tuning de bert-base-multilingual-cased pour NER.
F1 attendu : ~0.92 avec 300+ exemples augmentés.

Installation:
    pip install transformers datasets seqeval torch accelerate

Usage:
    python scripts/train_bert.py                    # entraîne si absent
    python scripts/train_bert.py --train            # force le ré-entraînement
    python scripts/train_bert.py --augment 500      # avec augmentation
    python scripts/train_bert.py --epochs 15        # plus d'époques
"""

import sys
import json
import argparse
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.normalization import postprocess
from data.train_data      import TRAIN_DATA
from scripts.augment      import augment_dataset, dataset_stats

# ── Imports optionnels ────────────────────────────────────────
try:
    from datasets import Dataset
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        TrainingArguments,
        Trainer,
        DataCollatorForTokenClassification,
        pipeline as hf_pipeline,
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠  transformers manquant — pip install transformers datasets torch accelerate")

try:
    from seqeval.metrics import classification_report as seq_report
    HAS_SEQEVAL = True
except ImportError:
    HAS_SEQEVAL = False
    print("⚠  seqeval manquant — pip install seqeval")


# ─────────────────────────────────────────────────────────────
# LABELS BIO
# ─────────────────────────────────────────────────────────────

LABELS = [
    "O",
    "B-DESTINATION", "I-DESTINATION",
    "B-DEPARTURE",   "I-DEPARTURE",
    "B-DATE",        "I-DATE",
    "B-TIME",        "I-TIME",
]
LABEL2ID: dict[str, int] = {l: i for i, l in enumerate(LABELS)}
ID2LABEL:  dict[int, str] = {i: l for l, i in LABEL2ID.items()}

MODEL_NAME = "bert-base-multilingual-cased"


# ─────────────────────────────────────────────────────────────
# CONVERSION SPANS → BIO
# ─────────────────────────────────────────────────────────────

def spacy_to_bio(text: str, entities: list, tokenizer) -> dict:
    """
    Convertit des spans (start, end, label) en séquence de labels BIO
    alignée sur les tokens BERT.
    """
    encoding = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=128,
    )
    offsets = encoding["offset_mapping"]

    # Tableau de labels au niveau caractère
    char_labels = ["O"] * len(text)
    for start, end, label in entities:
        for i in range(start, min(end, len(text))):
            char_labels[i] = f"B-{label}" if i == start else f"I-{label}"

    # Alignement tokens
    token_labels: list[int] = []
    prev_label = "O"
    for token_start, token_end in offsets:
        if token_start == token_end:          # token spécial [CLS] / [SEP]
            token_labels.append(-100)
            continue
        tok_label = char_labels[token_start]
        # Corriger I- isolé (sans B- précédent du même type)
        if tok_label.startswith("I-") and not prev_label.endswith(tok_label[2:]):
            tok_label = "B-" + tok_label[2:]
        token_labels.append(LABEL2ID.get(tok_label, 0))
        prev_label = tok_label

    encoding["labels"] = token_labels
    encoding.pop("offset_mapping")
    return dict(encoding)


def build_hf_dataset(train_data: list, tokenizer) -> "Dataset":
    records = []
    for text, ann in train_data:
        enc = spacy_to_bio(text, ann["entities"], tokenizer)
        records.append(enc)
    return Dataset.from_list(records)


# ─────────────────────────────────────────────────────────────
# MÉTRIQUES
# ─────────────────────────────────────────────────────────────

def compute_metrics(p) -> dict:
    if not HAS_SEQEVAL:
        return {}
    predictions, labels = p
    preds = np.argmax(predictions, axis=2)

    true_labels, true_preds = [], []
    for pred_seq, label_seq in zip(preds, labels):
        tl, tp = [], []
        for pred, label in zip(pred_seq, label_seq):
            if label != -100:
                tl.append(ID2LABEL[label])
                tp.append(ID2LABEL[pred])
        true_labels.append(tl)
        true_preds.append(tp)

    report = seq_report(true_labels, true_preds, output_dict=True)
    return {
        "precision": report["weighted avg"]["precision"],
        "recall":    report["weighted avg"]["recall"],
        "f1":        report["weighted avg"]["f1-score"],
    }


# ─────────────────────────────────────────────────────────────
# ENTRAÎNEMENT
# ─────────────────────────────────────────────────────────────

def train_bert(
    train_data:  list,
    output_dir:  str   = "models/bert",
    epochs:      int   = 10,
    lr:          float = 2e-5,
    batch_size:  int   = 8,
) -> "Trainer":
    """
    Fine-tune bert-base-multilingual-cased sur train_data.
    Sauvegarde le modèle dans output_dir.
    """
    if not HAS_TRANSFORMERS:
        raise ImportError("pip install transformers datasets torch accelerate")

    out = ROOT / output_dir
    print(f"📥  Tokenizer : {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("🔄  Construction du dataset HuggingFace…")
    dataset = build_hf_dataset(train_data, tokenizer)
    split   = dataset.train_test_split(test_size=0.2, seed=42)
    print(f"    {len(split['train'])} train | {len(split['test'])} eval")

    print("🏗   Chargement du modèle BERT…")
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    training_args = TrainingArguments(
        output_dir=str(out),
        num_train_epochs=epochs,
        learning_rate=lr,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1" if HAS_SEQEVAL else "loss",
        logging_steps=10,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
        processing_class=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer),
        compute_metrics=compute_metrics,
    )

    print(f"\n🚀  Fine-tuning BERT — {epochs} époques\n")
    trainer.train()
    trainer.save_model(str(out))
    tokenizer.save_pretrained(str(out))
    print(f"\n✅  Modèle BERT sauvegardé → {out}/")
    return trainer


# ─────────────────────────────────────────────────────────────
# INFÉRENCE
# ─────────────────────────────────────────────────────────────

def predict_bert(text: str, model_path: str = "models/bert") -> dict:
    """
    Extrait les entités via le pipeline HuggingFace token-classification.
    Retourne le résultat normalisé.
    """
    if not HAS_TRANSFORMERS:
        raise ImportError("pip install transformers")

    pipe = hf_pipeline(
        "token-classification",
        model=str(ROOT / model_path),
        aggregation_strategy="simple",
    )
    entities = pipe(text)
    raw = {"destination": None, "departure": None, "date": None, "time": None}
    for ent in entities:
        field = ent["entity_group"].lower()
        if field in raw and raw[field] is None:
            raw[field] = ent["word"].strip()
    return postprocess(raw, text)


# ─────────────────────────────────────────────────────────────
# DEMO SENTENCES
# ─────────────────────────────────────────────────────────────

DEMO_SENTENCES = [
    "nheb nemchi hammamet ghodwa 18h",
    "je veux aller a tunis demain matin",
    "take me to the airport tonight at 22h",
    "من هنا إلى سوسة غدا في المساء",
    "taxi men sfax lel lac ghodwa 18h",
    "reserver un taxi de la marsa vers le centre vendredi a 14h30",
]


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MOVIROO — Fine-tuning BERT NER")
    parser.add_argument("--train",   action="store_true",
                        help="Forcer le ré-entraînement")
    parser.add_argument("--model",   default="models/bert",
                        help="Chemin du modèle (défaut: models/bert)")
    parser.add_argument("--epochs",  type=int, default=10)
    parser.add_argument("--augment", type=int, default=0,
                        help="Nombre d'exemples synthétiques à ajouter")
    args = parser.parse_args()

    model_path = ROOT / args.model

    if model_path.exists() and not args.train:
        print(f"📦  Modèle BERT existant : {model_path}/")
    else:
        data = list(TRAIN_DATA)
        if args.augment > 0:
            print(f"🔄  Augmentation : +{args.augment} exemples…")
            data = augment_dataset(data, n=args.augment)
        dataset_stats(data, "Dataset d'entraînement BERT")
        train_bert(data, output_dir=args.model, epochs=args.epochs)

    print(f"\n🧪  Inférence BERT\n{'─'*60}")
    for sentence in DEMO_SENTENCES:
        result = predict_bert(sentence, args.model)
        print(f"\n📝  {sentence}")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()