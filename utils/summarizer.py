"""
utils/summarizer.py
Summarizes a transcript using a local Ollama model (llama3.2).
Requires Ollama to be running: https://ollama.com
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"
MAX_CHARS = 12_000


def summarize_transcript(transcript: str, video_title: str = "", model: str = DEFAULT_MODEL) -> str:
    truncated = transcript[:MAX_CHARS]
    if len(transcript) > MAX_CHARS:
        truncated += "\n\n[Transcript truncated]"

    title_line = f'Video title: "{video_title}"\n\n' if video_title else ""

    prompt = (
        f"{title_line}"
        f"Here is the transcript of a YouTube video:\n\n"
        f"{truncated}\n\n"
        "Write a clear, concise summary of this video in 3 to 5 sentences. "
        "Cover the main topic, key points, and any important conclusions. "
        "Plain paragraph only — no bullet points, no headers."
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Ollama HTTP error: {e}")

    data = response.json()
    summary: str = data.get("response", "").strip()

    if not summary:
        raise RuntimeError("Ollama returned an empty response. Is the model pulled?")

    return summary