import whisper
import numpy as np
from loguru import logger
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

class STT:
    def __init__(self, config):
        device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("tiny.en", device=device)
        self.sample_rate = 16000

    def transcribe(self, audio_data):
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            if np.max(np.abs(audio_array)) < 0.01:
                logger.warning("Audio too quiet, skipping transcription")
                return None
            result = self.model.transcribe(audio_array, fp16=TORCH_AVAILABLE and torch.cuda.is_available())
            text = result["text"].strip()
            if not text or len(text) > 100 or any(c not in 'abcdefghijklmnopqrstuvwxyz .,!?' for c in text.lower()):
                logger.warning(f"Invalid transcription: {text}")
                return None
            return text
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None