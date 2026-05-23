"""
utils/downloader.py
Downloads audio from a YouTube URL using yt-dlp.
Returns (audio_path, video_title, duration_seconds).
"""

import os
import tempfile
import yt_dlp


def download_audio(url: str) -> tuple[str, str, int]:
    tmp_dir = tempfile.mkdtemp()
    output_template = os.path.join(tmp_dir, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as e:
            raise ValueError(f"Could not download video: {e}") from e

    video_title: str = info.get("title", "Unknown Title")
    duration: int = int(info.get("duration", 0))
    video_id: str = info.get("id", "")

    audio_path = os.path.join(tmp_dir, f"{video_id}.mp3")
    if not os.path.exists(audio_path):
        mp3_files = [f for f in os.listdir(tmp_dir) if f.endswith(".mp3")]
        if not mp3_files:
            raise RuntimeError("Audio file not found after download.")
        audio_path = os.path.join(tmp_dir, mp3_files[0])

    return audio_path, video_title, duration