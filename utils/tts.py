"""
utils/tts.py
Converts text to speech using Coqui XTTS-v2.
Clones voice from a reference audio sample.
"""

import os
import tempfile
from TTS.api import TTS

# Module-level cache — avoid reloading model on every run
_tts = None

VOICE_SAMPLE = os.path.join(os.path.dirname(__file__), "..", "assets", "my_voice.wav")


def _load_model() -> TTS:
    global _tts
    if _tts is None:
        _tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    return _tts


def text_to_speech(text: str, output_path: str = None) -> str:
    """
    Convert text to speech using your cloned voice.

    Args:
        text        : Text to speak.
        output_path : Where to save the .wav file.
                      If None, a temp file is created.

    Returns:
        Path to the generated .wav audio file.
    """
    if not os.path.exists(VOICE_SAMPLE):
        raise FileNotFoundError(
            f"Voice sample not found at {VOICE_SAMPLE}. "
            "Make sure assets/my_voice.m4a exists."
        )

    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        output_path = tmp.name
        tmp.close()

    tts = _load_model()

    tts.tts_to_file(
        text=text,
        speaker_wav=VOICE_SAMPLE,
        language="en",
        file_path=output_path,
    )

    return output_path