"""
utils/transcript_fetcher.py
Fetches YouTube transcript/captions directly without downloading audio.
"""

from youtube_transcript_api import YouTubeTranscriptApi
import re


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

    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        transcript = " ".join([t.text for t in fetched])
        return transcript, video_id
    except Exception as e:
        raise RuntimeError(
            f"Could not fetch transcript: {e}\n"
            "The video may not have captions available."
        )