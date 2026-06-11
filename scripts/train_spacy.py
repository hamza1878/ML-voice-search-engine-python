"""
MOVIROO — scripts/train_spacy.py

Entraînement d'un modèle spaCy NER multilingue (blank "xx").

Usage:
    python scripts/train_spacy.py                   # entraîne ou charge
    python scripts/train_spacy.py --train           # force le ré-entraînement
    python scripts/train_spacy.py --augment 500     # +500 exemples synthétiques
    python scripts/train_spacy.py --iter 200        # plus d'itérations
    python scripts/train_spacy.py --interactive     # mode interactif après entraînement
"""

import sys
import json
import random
import warnings
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import spacy
from spacy.training import Example
from spacy.util    import minibatch, compounding

from config.normalization import postprocess
from data.train_data      import TRAIN_DATA
from scripts.augment      import augment_dataset, dataset_stats

# ─────────────────────────────────────────────────────────────
# ENTRAÎNEMENT
# ─────────────────────────────────────────────────────────────
if spacy.prefer_gpu():
    print("🚀 GPU activé")
else:
    print("💻 CPU utilisé")
spacy.prefer_gpu() 
def train_spacy(
    train_data:  list[tuple],
    n_iter:      int   = 150,
    output_path: str   = "models/spacy",
    dropout:     float = 0.3,
) -> spacy.language.Language:
    """
    Entraîne un modèle spaCy NER sur train_data.
    Sauvegarde le modèle dans output_path et le retourne.
    """
    nlp = spacy.blank("xx")
    ner = nlp.add_pipe("ner", last=True)

    # Enregistrement des labels
    for _, ann in train_data:
        for _, _, label in ann["entities"]:
            ner.add_label(label)

    # Construction des Examples spaCy
    examples: list[Example] = []
    skipped = 0
    for text, ann in train_data:
        doc = nlp.make_doc(text)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ex = Example.from_dict(doc, ann)
            examples.append(ex)
        except Exception as e:
            print(f"  ⚠  Ignoré : {text[:50]!r} → {e}")
            skipped += 1

    print(f"  ✓ {len(examples)} exemples valides ({skipped} ignorés)")

    # Initialisation
    optimizer    = nlp.initialize(lambda: examples)
    other_pipes  = [p for p in nlp.pipe_names if p != "ner"]

    print(f"\n🚀  Entraînement spaCy — {n_iter} itérations\n")
    with nlp.disable_pipes(*other_pipes):
        for i in range(n_iter):
            random.shuffle(examples)
            losses: dict[str, float] = {}
            for batch in minibatch(examples, size=compounding(2.0, 16.0, 1.001)):
                nlp.update(batch, sgd=optimizer, drop=dropout, losses=losses)
            if i % 25 == 0 or i == n_iter - 1:
                print(f"  iter {i:4d} | loss NER : {losses.get('ner', 0):.4f}")

    # Sauvegarde
    out = ROOT / output_path
    out.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(out)
    print(f"\n✅  Modèle spaCy sauvegardé → {out}/")
    return nlp


# ─────────────────────────────────────────────────────────────
# ÉVALUATION
# ─────────────────────────────────────────────────────────────

def evaluate(nlp: spacy.language.Language, test_data: list[tuple]) -> dict:
    """
    Calcule Précision / Rappel / F1 sur test_data.
    Comparaison stricte (start, end, label).
    """
    tp = fp = fn = 0
    for text, ann in test_data:
        doc   = nlp(text)
        pred  = {(e.start_char, e.end_char, e.label_) for e in doc.ents}
        true  = {(s, e, l) for s, e, l in ann["entities"]}
        tp   += len(pred & true)
        fp   += len(pred - true)
        fn   += len(true - pred)

    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return {"precision": round(p, 3), "recall": round(r, 3), "f1": round(f, 3)}


# ─────────────────────────────────────────────────────────────
# INFÉRENCE
# ─────────────────────────────────────────────────────────────

# def predict(nlp: spacy.language.Language, text: str) -> dict:
#     """
#     Extrait les entités d'un texte et retourne le résultat normalisé.
#     """
#     doc = nlp(text)
#     raw = {"destination": None, "departure": None, "date": None, "time": None}
#     for ent in doc.ents:
#         field = ent.label_.lower()
#         if field in raw and raw[field] is None:
#             raw[field] = ent.text
#     return postprocess(raw, text)
from config.knowledge import DATE_KEYWORDS

def predict(nlp: spacy.language.Language, text: str) -> dict:
    doc = nlp(text)

    raw = {
        "destination": None,
        "departure": None,
        "date": None,
        "time": None
    }

    for ent in doc.ents:
        ent_text = ent.text.lower()

        # 🔥 PRIORITÉ DATE (override ML)
        if ent_text in DATE_KEYWORDS:
            raw["date"] = ent_text
            continue

        field = ent.label_.lower()

        if field in raw and raw[field] is None:
            raw[field] = ent.text

    return postprocess(raw, text)

# ─────────────────────────────────────────────────────────────
# MODE INTERACTIF
# ─────────────────────────────────────────────────────────────

def interactive_loop(nlp: spacy.language.Language) -> None:
    SEP = "─" * 60
    print(f"\n{SEP}\n💬  Mode interactif (q pour quitter)\n{SEP}\n")
    while True:
        try:
            ui = input("📝 > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not ui or ui.lower() in ("q", "quit", "exit"):
            break
        result = predict(nlp, ui)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()


# ─────────────────────────────────────────────────────────────
# DEMO SENTENCES
# ─────────────────────────────────────────────────────────────

DEMO_SENTENCES = [
    "nheb nimchi il touns men hammamet ghodwa 18h",
    "nheb nemchi hammamet ghodwa 18h",
    "nemchi sfax min el-maktab el-khamis ba3d dhuhr",
    "taxi men ennasr lel lac tawwa",
    "je veux aller a tunis demain matin",
    "taxi depuis bizerte vers sfax samedi 9h",
    "reserver un taxi de la marsa vers le centre vendredi a 14h30",
    "take me to the airport tonight at 22h",
    "I need a taxi from sfax to sousse tomorrow at 8h30",
    "book a ride to monastir next monday at 7h",
    "من هنا إلى سوسة غدا في المساء",
    "احتاج تاكسي من المكتب إلى المطار غدا",
    "تاكسي إلى بنزرت يوم الأربعاء في المساء",
]


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MOVIROO — Entraînement spaCy NER")
    parser.add_argument("--train",       action="store_true",
                        help="Forcer le ré-entraînement même si le modèle existe")
    parser.add_argument("--interactive", action="store_true",
                        help="Lancer le mode interactif après entraînement")
    parser.add_argument("--model",       default="models/spacy",
                        help="Chemin du modèle (défaut: models/spacy)")
    parser.add_argument("--iter",        type=int, default=150,
                        help="Nombre d'itérations (défaut: 150)")
    parser.add_argument("--augment",     type=int, default=0,
                        help="Nombre d'exemples synthétiques à ajouter")
    args = parser.parse_args()

    model_path = ROOT / args.model

    # ── Chargement ou entraînement ────────────────────────────
    if model_path.exists() and not args.train:
        print(f"📦  Chargement du modèle : {model_path}/")
        nlp = spacy.load(model_path)
    else:
        data = list(TRAIN_DATA)
        if args.augment > 0:
            print(f"🔄  Augmentation : +{args.augment} exemples synthétiques…")
            data = augment_dataset(data, n=args.augment)
        dataset_stats(data, "Dataset d'entraînement")

        random.seed(42)
        random.shuffle(data)
        split = int(len(data) * 0.8)
        train_set, test_set = data[:split], data[split:]
        print(f"📊  {len(train_set)} train | {len(test_set)} test")

        nlp = train_spacy(train_set, n_iter=args.iter, output_path=args.model)

        if test_set:
            metrics = evaluate(nlp, test_set)
            print(f"\n📈  Évaluation → P={metrics['precision']}  R={metrics['recall']}  F1={metrics['f1']}")

    # ── Démo ──────────────────────────────────────────────────
    print(f"\n{'─'*60}\n🧪  Inférence démo\n{'─'*60}")
    for sentence in DEMO_SENTENCES:
        r = predict(nlp, sentence)
        print(f"\n📝  {sentence}")
        print(f"     dest={r['destination']}  dep={r['departure']}")
        print(f"     date={r['date']}         time={r['time']}")
        if r["missing_fields"]:
            print(f"     ⚠   manquants : {r['missing_fields']}")

    if args.interactive:
        interactive_loop(nlp)


if __name__ == "__main__":
    main()