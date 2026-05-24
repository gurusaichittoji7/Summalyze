"""
utils/transcript_fetcher.py
Fetches YouTube transcript using RapidAPI YouTube Transcript API.
"""

import os
import re
import requests


def get_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL."""
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Could not extract video ID from URL.")


def fetch_transcript(url: str) -> tuple[str, str]:
    video_id = get_video_id(url)

    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise EnvironmentError("RAPIDAPI_KEY is not set.")

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "youtube-transcript3.p.rapidapi.com",
        "x-rapidapi-key": api_key,
    }

    response = requests.get(
        f"https://youtube-transcript3.p.rapidapi.com/api/transcript",
        headers=headers,
        params={"videoId": video_id},
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"RapidAPI error {response.status_code}: {response.text}"
        )

    data = response.json()

    # Extract transcript text from response
    segments = data.get("transcript", [])
    if not segments:
        raise RuntimeError("No transcript found for this video.")

    transcript = " ".join([s.get("text", "") for s in segments])
    return transcript, video_id