import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

SR = 16000          # sample rate
DURATION = 4        # seconds
LANG = "fr"         # force French

model = WhisperModel("small", device="cpu", compute_type="int8")

def record_audio(seconds=DURATION, sr=SR):
    print(f"🎙️ Parle maintenant ({seconds}s)...")
    audio = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten()

def transcribe(audio_np):
    segments, info = model.transcribe(audio_np, language=LANG, vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text

if __name__ == "__main__":
    audio = record_audio()
    text = transcribe(audio)
    print("✅ STT ->", text if text else "[rien détecté]")