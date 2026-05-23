import streamlit as st
import os
from utils.downloader import download_audio
from utils.transcriber import transcribe_audio
from utils.summarizer import summarize_transcript

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Summalyze",
    page_icon="⚡",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Fira+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #f5f2eb; color: #1a1a1a; }

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.6rem;
    font-weight: 700;
    letter-spacing: -3px;
    line-height: 1;
    color: #1a1a1a;
    margin-bottom: 0.3rem;
}
.hero-title span { color: #d4500a; }
.hero-sub { font-size: 0.92rem; color: #666; margin-bottom: 1.5rem; }

.tag-row { display: flex; gap: 0.5rem; margin-bottom: 1.8rem; flex-wrap: wrap; }
.tag {
    font-family: 'Fira Mono', monospace;
    font-size: 0.68rem;
    border: 1px solid #c5c0b5;
    border-radius: 3px;
    padding: 0.2rem 0.55rem;
    color: #888;
}

.step-label {
    font-family: 'Fira Mono', monospace;
    font-size: 0.7rem;
    color: #d4500a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.4rem 0 0.3rem 0;
}

.summary-outer {
    border: 2px solid #1a1a1a;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 1.8rem;
}
.summary-header {
    background: #1a1a1a;
    color: #f5f2eb;
    font-family: 'Fira Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.5rem 1rem;
}
.summary-body {
    padding: 1.4rem 1.6rem;
    font-size: 1.0rem;
    line-height: 1.8;
    color: #1a1a1a;
    background: #faf8f3;
}

.meta-row { display: flex; gap: 0.6rem; margin: 0.8rem 0 0.2rem; flex-wrap: wrap; }
.meta-pill {
    font-family: 'Fira Mono', monospace;
    font-size: 0.72rem;
    background: #ede9e0;
    border: 1px solid #c5c0b5;
    border-radius: 20px;
    padding: 0.22rem 0.75rem;
    color: #555;
}

.stTextInput > div > div > input {
    background: #faf8f3 !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 4px !important;
    color: #1a1a1a !important;
    font-family: 'Fira Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 0.75rem 1rem !important;
    box-shadow: 3px 3px 0px #1a1a1a !important;
}
.stTextInput > div > div > input:focus {
    border-color: #d4500a !important;
    box-shadow: 3px 3px 0px #d4500a !important;
}

.stButton > button {
    background: #1a1a1a !important;
    color: #f5f2eb !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 4px !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 3px 3px 0px #d4500a !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #d4500a !important;
    border-color: #d4500a !important;
    box-shadow: 3px 3px 0px #1a1a1a !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-bottom: 2px solid #1a1a1a; padding-bottom: 1.4rem; margin-bottom: 2rem;">
    <div class="hero-title">Summa<span>lyze</span></div>
    <div class="hero-sub">Drop a YouTube URL. Get the gist. No fluff.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="tag-row">
    <span class="tag">whisper</span>
    <span class="tag">ollama / llama3.2</span>
    <span class="tag">100% local</span>
    <span class="tag">free</span>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
url = st.text_input(
    label="YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 4])
with col1:
    run = st.button("⚡ Run")

# ── Pipeline ──────────────────────────────────────────────────────────────────
if run:
    if not url.strip():
        st.warning("Please enter a YouTube URL.")
    else:
        audio_path = None
        try:
            # Step 1 — Download
            st.markdown('<div class="step-label">▸ step 01 — downloading audio</div>', unsafe_allow_html=True)
            with st.spinner("Fetching audio from YouTube…"):
                audio_path, video_title, duration_sec = download_audio(url)
            st.success(f"✓  {video_title}")

            # Step 2 — Transcribe
            st.markdown('<div class="step-label">▸ step 02 — transcribing with whisper</div>', unsafe_allow_html=True)
            with st.spinner("Running Whisper locally…"):
                transcript = transcribe_audio(audio_path)

            minutes, seconds = divmod(duration_sec, 60)
            st.markdown(
                f'<div class="meta-row">'
                f'<span class="meta-pill">⏱ {minutes}m {seconds}s</span>'
                f'<span class="meta-pill">📝 {len(transcript.split()):,} words</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Step 3 — Summarize
            st.markdown('<div class="step-label">▸ step 03 — summarizing with llama3.2</div>', unsafe_allow_html=True)
            with st.spinner("Asking Ollama to summarize…"):
                summary = summarize_transcript(transcript, video_title)

            st.markdown(
                f'<div class="summary-outer">'
                f'<div class="summary-header">⚡ summary</div>'
                f'<div class="summary-body">{summary}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            with st.expander("view full transcript"):
                st.text_area("", transcript, height=280, label_visibility="collapsed")

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)