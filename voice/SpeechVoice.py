# from faster_whisper import WhisperModel

# model = WhisperModel("tiny", device="cpu", compute_type="int8")
# segments, _ = model.transcribe("voice/test3.mp3", language="ar")
# text = " ".join([seg.text for seg in segments])
# print(text)
# Install the requests package by executing the command "pip install requests"
import requests

headers = {"authorization": "01fd3280e213401fa1e6da42aa2a02e2"}

with open(r"C:\Users\hamzabensassi\Desktop\train_voice_ml_contorle\voice\test.mp3", "rb") as f:
    response = requests.post("https://api.assemblyai.com/v2/upload", headers=headers, data=f)
audio_url = response.json()["upload_url"]
print("Uploaded audio URL:", audio_url)
data = {
    "audio_url": audio_url,
    "language_detection": True, 
    "speech_models": ["universal-3-pro", "universal-2"] 
}


response = requests.post("https://api.assemblyai.com/v2/transcript", json=data, headers=headers)
transcript_id = response.json()['id']

polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

import time
while True:
    transcription_result = requests.get(polling_endpoint, headers=headers).json()
    if transcription_result['status'] == 'completed':
        print("Transcript Text:", transcription_result['text'])
        break
    elif transcription_result['status'] == 'error':
        raise RuntimeError(f"Transcription failed: {transcription_result['error']}")
    else:
        time.sleep(3)