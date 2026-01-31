import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class WhisperSTT:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        sample_rate: int = 16000,
        record_seconds: int = 4,
        language: str = "en",  # ✅ force English
    ):
        self.sr = sample_rate
        self.seconds = record_seconds
        self.language = language
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def record_audio(self, seconds: int | None = None) -> np.ndarray:
        secs = seconds if seconds is not None else self.seconds
        audio = sd.rec(int(secs * self.sr), samplerate=self.sr, channels=1, dtype="float32")
        sd.wait()
        return audio.flatten()

    def transcribe(self, audio_np: np.ndarray) -> str:
        segments, info = self.model.transcribe(
            audio_np,
            language=self.language,     # ✅ "en"
            vad_filter=True,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text

    def listen_once(self) -> str:
        audio = self.record_audio()
        return self.transcribe(audio)