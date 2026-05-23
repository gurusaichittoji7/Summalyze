"""
utils/transcriber.py
Transcribes audio using OpenAI Whisper running locally.
"""

import os
import whisper

_model = None


def _load_model(model_size: str = "base") -> whisper.Whisper:
    global _model
    if _model is None:
        _model = whisper.load_model(model_size)
    return _model


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = _load_model(model_size)

    try:
        result = model.transcribe(audio_path, fp16=False)
    except Exception as e:
        raise RuntimeError(f"Whisper transcription failed: {e}") from e

    transcript: str = result.get("text", "").strip()

    if not transcript:
        raise RuntimeError("Whisper returned an empty transcript.")

    return transcript