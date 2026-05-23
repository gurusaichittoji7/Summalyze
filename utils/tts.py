"""
utils/tts.py
Converts text to speech using gTTS (Google Text-to-Speech).
"""

import os
import tempfile
from gtts import gTTS


def text_to_speech(text: str, output_path: str = None) -> str:
    """
    Convert text to speech using gTTS.

    Args:
        text        : Text to speak.
        output_path : Where to save the .mp3 file.

    Returns:
        Path to the generated .mp3 audio file.
    """
    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        output_path = tmp.name
        tmp.close()

    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)

    return output_path