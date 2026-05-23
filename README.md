# ⚡ Summalyze
Drop a YouTube URL or audio file. Get the gist. No fluff.

## Live Demo
https://summalyze-yt.streamlit.app/

## Features
- 🎬 YouTube URL summarization (local only)
- 🎙️ Audio file upload summarization (cloud + local)
- 🔊 Summary read back as audio

## Stack
| Layer | Tool |
|---|---|
| Audio download | yt-dlp |
| Transcription | Whisper (local) |
| Summarization | Groq / llama-3.1-8b |
| Text-to-speech | gTTS |
| UI | Streamlit |

## Run locally
- pip install -r requirements.txt

- streamlit run app.py