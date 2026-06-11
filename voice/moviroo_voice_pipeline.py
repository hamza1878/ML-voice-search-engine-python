
"""
╔══════════════════════════════════════════════════════════╗
║       MOVIROO — Voice → NER Pipeline                     ║
║       AssemblyAI STT  +  BERT/spaCy NER                  ║
║                                                          ║
║  Supports: TN dialect · AR · FR · EN                     ║
╚══════════════════════════════════════════════════════════╝

Install:
    

Usage:
    python moviroo_voice_pipeline.py --audio voice/test3.mp3
    python moviroo_voice_pipeline.py --audio voice/test3.mp3 --model bert
    python moviroo_voice_pipeline.py  ← interactive mic loop (no file)
"""

import sys
import time
import json
import argparse
import requests
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# ── AssemblyAI config ─────────────────────────────────────
ASSEMBLYAI_KEY  = "01fd3280e213401fa1e6da42aa2a02e2"   # ← your key
UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_URL  = "https://api.assemblyai.com/v2/transcript"
HEADERS         = {"authorization": ASSEMBLYAI_KEY}


def upload_audio(file_path: str) -> str:
    """Upload an audio file → return hosted URL."""
    print(f"📤 Uploading: {file_path}")
    with open(file_path, "rb") as f:
        resp = requests.post(UPLOAD_ENDPOINT, headers=HEADERS, data=f)
    resp.raise_for_status()
    url = resp.json()["upload_url"]
    print(f"   ✅ Uploaded → {url[:60]}...")
    return url

def transcribe(audio_url: str, language_code: str = None) -> str:
    payload = {
    "audio_url": audio_url,
    "speech_models": ["universal-2"],   # ← liste, pas string
}

    if language_code:
        payload["language_code"] = language_code
    else:
        payload["language_detection"] = True  # ← auto-detect si pas de lang

    print("🎙  Submitting transcription job...")
    resp = requests.post(TRANSCRIPT_URL, json=payload, headers=HEADERS)

    if resp.status_code != 200:
        print("❌ ERROR RESPONSE:", resp.text)

    resp.raise_for_status()
    transcript_id = resp.json()["id"]

    # Poll until done
    poll_url = f"{TRANSCRIPT_URL}/{transcript_id}"
    print("⏳ Waiting for transcription", end="", flush=True)
    while True:
        result = requests.get(poll_url, headers=HEADERS).json()
        status = result["status"]
        if status == "completed":
            print(f"\n✅ Done!")
            return result["text"]
        elif status == "error":
            raise RuntimeError(f"❌ Transcription failed: {result['error']}")
        else:
            print(".", end="", flush=True)
            time.sleep(3)
def speech_to_text(file_path: str, language_code: str = None) -> str:
    """Full pipeline: file → AssemblyAI → transcript text."""
    audio_url = upload_audio(file_path)
    return transcribe(audio_url, language_code)


# ─────────────────────────────────────────────────────────
# 2. NER EXTRACTION
# ─────────────────────────────────────────────────────────

def load_ner(model_type: str = "bert"):
    """Load the NER model (spacy or bert)."""
    if model_type == "bert":
        from scripts.train_bert import predict_bert
        print("🤖 Using BERT NER")
        return lambda text: predict_bert(text, model_path="models/bert")

    else:
        import spacy
        from scripts.train_spacy import predict as predict_spacy
        from config.normalization import postprocess
        model_path = ROOT / "models/spacy"
        print(f"🤖 Loading spaCy model from {model_path}/")
        nlp = spacy.load(model_path)
        return lambda text: postprocess(predict_spacy(nlp, text), text)

# ─────────────────────────────────────────────────────────
# 3. FULL PIPELINE
# ─────────────────────────────────────────────────────────

def process_audio(file_path: str, predict_fn, language_code: str = None) -> dict:
    """
    Full pipeline:
      audio file → STT → NER → structured JSON

    Returns dict with keys: transcript, destination, departure, date, time, missing_fields
    """
    print(f"\n{'─'*55}")
    print(f"🎵 Processing: {file_path}")
    print(f"{'─'*55}")

    # Step 1: transcribe
    transcript = speech_to_text(file_path, language_code)
    print(f"\n📝 Transcript: {transcript}")

    # Step 2: NER
    print(f"\n🔍 Running NER...")
    result = predict_fn(transcript)

    # Attach transcript to result
    result["transcript"] = transcript

    return result


# ─────────────────────────────────────────────────────────
# 4. MAIN
# ─────────────────────────────────────────────────────────

def print_result(result: dict):
    SEP = "─" * 55
    print(f"\n{SEP}")
    print(f"📊 EXTRACTION RESULT")
    print(SEP)
    print(f"  transcript  : {result.get('transcript', '')}")
    print(f"  destination : {result.get('destination')}")
    print(f"  departure   : {result.get('departure')}")
    print(f"  date        : {result.get('date')}")
    print(f"  time        : {result.get('time')}")
    if result.get("missing_fields"):
        print(f"  ⚠  missing  : {result['missing_fields']}")
    print(SEP)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moviroo Voice → NER Pipeline")
    parser.add_argument("--audio",    type=str, default=None,
                        help="Path to audio file (.mp3, .wav, .m4a ...)")
    parser.add_argument("--model",    choices=["spacy", "bert"], default="spacy",
                        help="NER model to use")
    parser.add_argument("--lang",     type=str, default=None,
                        help="Language code: ar / fr / en (default: auto-detect)")
    parser.add_argument("--text",     type=str, default=None,
                        help="Skip STT — run NER directly on this text (for testing)")
    cli = parser.parse_args()

    # Load NER model
    predict_fn = load_ner(cli.model)

    # ── Mode A: direct text test (no audio) ──────────────
    if cli.text:
        print(f"\n📝 Input text: {cli.text}")
        result = predict_fn(cli.text)
        result["transcript"] = cli.text
        print_result(result)

    # ── Mode B: single audio file ─────────────────────────
    elif cli.audio:
        result = process_audio(cli.audio, predict_fn, cli.lang)
        print_result(result)
        # Also dump full JSON
        print("\n📦 Full JSON:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # ── Mode C: interactive loop ─────────────────────────
    else:
        print("\n💬 Interactive mode — enter audio file path or text (q to quit)")
        print("   Examples:")
        print("     > voice/test3.mp3        ← transcribe + NER")
        print("     > text: nheb nemchi tunis ghodwa 18h  ← NER only")
        print()

        while True:
            try:
                inp = input("📝 > ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not inp or inp.lower() in ("q", "quit", "exit"):
                break

            if inp.startswith("text:"):
                # NER only, no STT
                text = inp[5:].strip()
                result = predict_fn(text)
                result["transcript"] = text
            elif Path(inp).exists():
                result = process_audio(inp, predict_fn, cli.lang)
            else:
                print(f"  ⚠  File not found: {inp}")
                continue

            print_result(result)