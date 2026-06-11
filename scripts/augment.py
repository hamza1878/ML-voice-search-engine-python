"""
MOVIROO — scripts/augment.py

Génération de variantes synthétiques depuis les templates.

Usage:
    python scripts/augment.py                  # stats + 5 exemples
    python scripts/augment.py --n 500          # 500 exemples
    python scripts/augment.py --export         # → data/augmented/
    python scripts/augment.py --lang FR        # seulement le français
    python scripts/augment.py --validate       # valide le dataset de base
    python scripts/augment.py --n 300 --export --only-synthetic
"""

import re
import sys
import csv
import json
import random
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.pools     import DESTINATIONS, DEPARTURES, DATES, TIMES, LANGUAGES
from config.templates import TEMPLATES
from data.train_data  import TRAIN_DATA


# ─────────────────────────────────────────────────────────────
# GÉNÉRATION D'UN EXEMPLE
# ─────────────────────────────────────────────────────────────

def generate_example(
    template: str,
    fields: list[tuple[str, str]],
    lang: str,
) -> tuple | None:
    """
    Remplit un template avec des valeurs aléatoires et retourne
    un exemple annoté (text, {"entities": [...]}) ou None si échec.
    """
    values: dict[str, str] = {}

    # ── Tirage des valeurs ────────────────────────────────────
    if any(f == "dep"  for f, _ in fields):
        values["dep"]  = random.choice(DEPARTURES.get(lang, DEPARTURES["EN"]))
    if any(f == "dest" for f, _ in fields):
        values["dest"] = random.choice(DESTINATIONS.get(lang, DESTINATIONS["EN"]))
    if any(f == "date" for f, _ in fields):
        values["date"] = random.choice(DATES.get(lang, DATES["EN"]))
    if any(f == "time" for f, _ in fields):
        values["time"] = random.choice(TIMES.get(lang, TIMES["EN"]))

    # ── Éviter dep == dest ────────────────────────────────────
    if "dep" in values and "dest" in values and values["dep"] == values["dest"]:
        pool = [d for d in DESTINATIONS.get(lang, DESTINATIONS["EN"]) if d != values["dep"]]
        if pool:
            values["dest"] = random.choice(pool)

    # ── Construction du texte ─────────────────────────────────
    try:
        text = template.format(**values)
    except KeyError:
        return None

    # ── Extraction des spans ──────────────────────────────────
    entities: list[tuple[int, int, str]] = []
    seen_spans: set[tuple[int, int]] = set()

    for field, label in fields:
        val = values.get(field)
        if val is None:
            continue
        start = text.find(val)
        if start == -1:
            return None
        span = (start, start + len(val))
        if span not in seen_spans:
            entities.append((span[0], span[1], label))
            seen_spans.add(span)

    return (text, {"entities": entities}) if entities else None


# ─────────────────────────────────────────────────────────────
# GÉNÉRATION D'UN DATASET
# ─────────────────────────────────────────────────────────────

def generate_dataset(
    n: int = 200,
    langs: list[str] | None = None,
    seed: int = 42,
) -> list[tuple]:
    """Génère n exemples synthétiques équilibrés entre les langues."""
    random.seed(seed)
    langs = langs or LANGUAGES
    available = {l: TEMPLATES[l] for l in langs if l in TEMPLATES}
    lang_list  = list(available.keys())

    generated: list[tuple] = []
    attempts   = 0
    max_tries  = n * 20

    while len(generated) < n and attempts < max_tries:
        lang              = random.choice(lang_list)
        template, fields  = random.choice(available[lang])
        ex                = generate_example(template, fields, lang)
        if ex:
            generated.append(ex)
        attempts += 1

    print(f"  ✓ {len(generated)}/{n} exemples générés ({attempts} tentatives)")
    return generated


def augment_dataset(
    base_data: list[tuple],
    n: int = 200,
    langs: list[str] | None = None,
    seed: int = 42,
) -> list[tuple]:
    """Concatène le dataset de base avec des exemples synthétiques."""
    synthetic = generate_dataset(n=n, langs=langs, seed=seed)
    return base_data + synthetic


# ─────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────

def validate_dataset(
    data: list[tuple],
    verbose: bool = True,
) -> tuple[list, list]:
    """
    Vérifie que chaque span (start, end) correspond bien au texte.
    Retourne (valid_examples, invalid_examples).
    """
    valid, invalid = [], []
    for text, ann in data:
        ok = True
        for start, end, label in ann["entities"]:
            if end > len(text) or not text[start:end].strip():
                if verbose:
                    print(f"  ✗ [{label} {start}:{end}] dans : {text[:55]!r}")
                ok = False
                break
        (valid if ok else invalid).append((text, ann))
    return valid, invalid


# ─────────────────────────────────────────────────────────────
# STATISTIQUES
# ─────────────────────────────────────────────────────────────

def dataset_stats(data: list[tuple], title: str = "Dataset") -> dict:
    """Affiche et retourne les statistiques du dataset."""
    label_counts: dict[str, int] = {}
    for _, ann in data:
        for _, _, label in ann["entities"]:
            label_counts[label] = label_counts.get(label, 0) + 1

    stats = {
        "total_examples": len(data),
        "total_entities": sum(label_counts.values()),
        "by_label":       label_counts,
    }

    print(f"\n📊  {title}")
    print(f"    Exemples : {stats['total_examples']}")
    print(f"    Entités  : {stats['total_entities']}")
    for label, count in sorted(label_counts.items()):
        bar = "█" * (count // max(1, stats["total_examples"] // 40))
        print(f"    {label:<15} : {count:5d}  {bar}")

    return stats


# ─────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────

def export_json(data: list[tuple], path: Path) -> None:
    """Exporte en JSON lisible par n'importe quel outil."""
    records = [
        {
            "text":     text,
            "entities": [
                {"start": s, "end": e, "label": l}
                for s, e, l in ann["entities"]
            ],
        }
        for text, ann in data
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅  JSON   → {path}  ({len(data)} exemples)")


def export_spacy_format(data: list[tuple], path: Path) -> None:
    """Format spans compatible avec spaCy DocBin."""
    records = [
        {
            "text":  text,
            "spans": [{"start": s, "end": e, "label": l} for s, e, l in ann["entities"]],
        }
        for text, ann in data
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅  spaCy  → {path}")


def export_csv(data: list[tuple], path: Path) -> None:
    """Export CSV plat : text, DESTINATION, DEPARTURE, DATE, TIME."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "DESTINATION", "DEPARTURE", "DATE", "TIME"])
        for text, ann in data:
            row = {"DESTINATION": "", "DEPARTURE": "", "DATE": "", "TIME": ""}
            for s, e, label in ann["entities"]:
                if label in row:
                    row[label] = text[s:e]
            writer.writerow([text, row["DESTINATION"], row["DEPARTURE"], row["DATE"], row["TIME"]])
    print(f"  ✅  CSV    → {path}")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MOVIROO — Augmentation du dataset")
    parser.add_argument("--n",             type=int,  default=200,
                        help="Nombre d'exemples synthétiques à générer (défaut: 200)")
    parser.add_argument("--lang",          type=str,  default=None,
                        help="Langue cible TN/FR/EN/AR (défaut: toutes)")
    parser.add_argument("--seed",          type=int,  default=42)
    parser.add_argument("--export",        action="store_true",
                        help="Exporter JSON + CSV + spaCy dans data/augmented/")
    parser.add_argument("--validate",      action="store_true",
                        help="Valider le dataset de base avant augmentation")
    parser.add_argument("--only-synthetic",action="store_true",
                        help="N'exporter que les exemples synthétiques")
    args = parser.parse_args()

    langs = [args.lang.upper()] if args.lang else None

    # ── Validation ────────────────────────────────────────────
    if args.validate:
        print("\n🔍  Validation du dataset de base…")
        valid, invalid = validate_dataset(TRAIN_DATA)
        print(f"    ✓ {len(valid)} valides  |  ✗ {len(invalid)} invalides")

    dataset_stats(TRAIN_DATA, "Dataset de base")

    # ── Génération ────────────────────────────────────────────
    print(f"\n🔄  Génération de {args.n} exemples synthétiques…")
    augmented = augment_dataset(TRAIN_DATA, n=args.n, langs=langs, seed=args.seed)
    synthetic = augmented[len(TRAIN_DATA):]
    dataset_stats(augmented, "Dataset augmenté (base + synthétique)")

    # ── Export ────────────────────────────────────────────────
    if args.export:
        out_dir    = ROOT / "data" / "augmented"
        to_export  = synthetic if args.only_synthetic else augmented
        label      = "synthétique" if args.only_synthetic else "complet"
        print(f"\n💾  Export du dataset {label} ({len(to_export)} exemples)…")
        export_json(to_export,         out_dir / "augmented.json")
        export_csv(to_export,          out_dir / "augmented.csv")
        export_spacy_format(to_export, out_dir / "augmented_spacy.json")

    # ── Aperçu ────────────────────────────────────────────────
    print(f"\n── Exemples synthétiques (5 aléatoires) ──")
    for text, ann in random.sample(synthetic, min(5, len(synthetic))):
        print(f"  📝  {text}")
        for s, e, l in ann["entities"]:
            print(f"       [{s}:{e}] {l:<15} → '{text[s:e]}'")
        print()


if __name__ == "__main__":
    main()