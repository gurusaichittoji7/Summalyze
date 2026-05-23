"""
utils/summarizer.py
Summarizes a transcript using Groq API (llama3 hosted).
"""

import os
from groq import Groq

MAX_CHARS = 12_000


def summarize_transcript(transcript: str, video_title: str = "") -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file or Streamlit secrets."
        )

    client = Groq(api_key=api_key)

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

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()