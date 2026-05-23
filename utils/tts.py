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


def _load_model():
    global _tts
    if _tts is None:
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import Xtts
        config = XttsConfig()
        config.load_json(
            os.path.expanduser(
                "~/Library/Application Support/tts/tts_models--multilingual--multi-dataset--xtts_v2/config.json"
            )
        )
        _tts = Xtts.init_from_config(config)
        _tts.load_checkpoint(
            config,
            checkpoint_dir=os.path.expanduser(
                "~/Library/Application Support/tts/tts_models--multilingual--multi-dataset--xtts_v2"
            ),
            eval=True,
        )
    return _tts


def text_to_speech(text: str, output_path: str = None) -> str:
    if not os.path.exists(VOICE_SAMPLE):
        raise FileNotFoundError(f"Voice sample not found at {VOICE_SAMPLE}.")

    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        output_path = tmp.name
        tmp.close()

    import torch
    import torchaudio

    model = _load_model()

    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=[VOICE_SAMPLE]
    )

    # Split text into sentences to stay under 400 token limit
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Group sentences into chunks of max ~200 chars
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) < 200:
            current += " " + sentence
        else:
            if current:
                chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())

    # Generate audio for each chunk
    wav_chunks = []
    for chunk in chunks:
        out = model.inference(
            text=chunk,
            language="en",
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=0.3,
            repetition_penalty=5.0,
            top_k=50,
            top_p=0.85,
        )
        wav_chunks.append(torch.tensor(out["wav"]))

    # Concatenate all chunks into one audio file
    full_wav = torch.cat(wav_chunks, dim=0).unsqueeze(0)
    torchaudio.save(output_path, full_wav, 24000)

    return output_path