import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from utils.transcriber import transcribe_audio
from utils.summarizer import summarize_transcript
from utils.downloader import download_audio

load_dotenv()

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

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #1a1a1a;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Fira Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #888 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.6rem 1.4rem !important;
    letter-spacing: 0.05em;
}
.stTabs [aria-selected="true"] {
    color: #1a1a1a !important;
    border-bottom: 2px solid #d4500a !important;
    background: transparent !important;
}

/* Input */
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

/* File uploader */
[data-testid="stFileUploader"] {
    background: #faf8f3 !important;
    border: 2px dashed #c5c0b5 !important;
    border-radius: 4px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #d4500a !important;
}

/* Button */
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
    <div class="hero-sub">Drop a YouTube URL or audio file. Get the gist. No fluff.</div>
</div>
""", unsafe_allow_html=True)

# ── Shared summary renderer ───────────────────────────────────────────────────
def render_summary(audio_path: str, title: str, duration_sec: int = 0):
    # Transcribe
    st.markdown('<div class="step-label">▸ step 01 — transcribing</div>', unsafe_allow_html=True)
    with st.spinner("Running Whisper locally…"):
        transcript = transcribe_audio(audio_path)

    if duration_sec:
        minutes, seconds = divmod(duration_sec, 60)
        st.markdown(
            f'<div class="meta-row">'
            f'<span class="meta-pill">⏱ {minutes}m {seconds}s</span>'
            f'<span class="meta-pill">📝 {len(transcript.split()):,} words</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="meta-row">'
            f'<span class="meta-pill">📝 {len(transcript.split()):,} words</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Summarize
    st.markdown('<div class="step-label">▸ step 02 — summarizing</div>', unsafe_allow_html=True)
    with st.spinner("Asking Ollama to summarize…"):
        summary = summarize_transcript(transcript, title)

    st.markdown(
        f'<div class="summary-outer">'
        f'<div class="summary-header">⚡ summary</div>'
        f'<div class="summary-body">{summary}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # TTS — convert summary to audio in your voice
    st.markdown('<div class="step-label">▸ step 03 — generating audio</div>', unsafe_allow_html=True)
    with st.spinner("Converting summary to your voice…"):
        from utils.tts import text_to_speech
        tts_path = text_to_speech(summary)

    with open(tts_path, "rb") as f:
        audio_bytes = f.read()

    st.markdown('<div class="step-label">▸ listen to summary</div>', unsafe_allow_html=True)
    st.audio(audio_bytes, format="audio/mp3")

    with st.expander("view full transcript"):
        st.text_area("", transcript, height=280, label_visibility="collapsed")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎬  YouTube URL", "🎙️  Audio File"])

# ── Tab 1: YouTube ────────────────────────────────────────────────────────────
with tab1:
    url = st.text_input(
        label="YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )
    col1, _ = st.columns([1, 4])
    with col1:
        run_yt = st.button("⚡ Run", key="yt_btn")

    if run_yt:
        if not url.strip():
            st.warning("Please enter a YouTube URL.")
        else:
            try:
                # Try transcript API first (works on cloud)
                st.markdown('<div class="step-label">▸ step 01 — fetching transcript</div>', unsafe_allow_html=True)
                with st.spinner("Fetching YouTube captions…"):
                    from utils.transcript_fetcher import fetch_transcript
                    transcript, video_id = fetch_transcript(url)
                st.success(f"✓ Transcript fetched")

                st.markdown(
                    f'<div class="meta-row">'
                    f'<span class="meta-pill">📝 {len(transcript.split()):,} words</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # Summarize
                st.markdown('<div class="step-label">▸ step 02 — summarizing</div>', unsafe_allow_html=True)
                with st.spinner("Summarizing…"):
                    summary = summarize_transcript(transcript, "")

                st.markdown(
                    f'<div class="summary-outer">'
                    f'<div class="summary-header">⚡ summary</div>'
                    f'<div class="summary-body">{summary}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # TTS
                st.markdown('<div class="step-label">▸ step 03 — generating audio</div>', unsafe_allow_html=True)
                with st.spinner("Converting summary to audio…"):
                    from utils.tts import text_to_speech
                    tts_path = text_to_speech(summary)

                with open(tts_path, "rb") as f:
                    audio_bytes = f.read()

                st.markdown('<div class="step-label">▸ listen to summary</div>', unsafe_allow_html=True)
                st.audio(audio_bytes, format="audio/mp3")

                with st.expander("view full transcript"):
                    st.text_area("", transcript, height=280, label_visibility="collapsed")

            except Exception as e:
                st.error(f"Error: {e}")

# ── Tab 2: Audio File ─────────────────────────────────────────────────────────
with tab2:
    uploaded_file = st.file_uploader(
        "Upload an audio file",
        type=["mp3", "wav", "m4a"],
        label_visibility="collapsed",
    )
    col1, _ = st.columns([1, 4])
    with col1:
        run_audio = st.button("⚡ Run", key="audio_btn")

    if run_audio:
        if uploaded_file is None:
            st.warning("Please upload an audio file first.")
        else:
            tmp_path = None
            try:
                # Save uploaded file to a temp path
                suffix = os.path.splitext(uploaded_file.name)[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                st.success(f"✓  {uploaded_file.name}")
                render_summary(tmp_path, uploaded_file.name)
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)