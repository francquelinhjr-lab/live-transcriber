import streamlit as st
import whisper
import tempfile
import os
import re

# ---------------------------------------------------------
# FRANCQUELIN LIVE SCRIBE
# ---------------------------------------------------------

st.set_page_config(
    page_title="Francquelin Live Scribe",
    page_icon="🎙️",
    layout="wide"
)

# ---------------------------------------------------------
# STYLE
# ---------------------------------------------------------

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 18px;
    margin-bottom: 30px;
}

.brand {
    text-align: right;
    font-weight: bold;
    font-size: 14px;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">🎙️ Francquelin Live Scribe</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Record lectures • Transcribe speech • Create study notes</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# LOAD WHISPER
# ---------------------------------------------------------

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")


# ---------------------------------------------------------
# MODEL SELECTION
# ---------------------------------------------------------

st.sidebar.header("⚙️ Settings")

model_size = st.sidebar.selectbox(
    "Transcription model",
    ["tiny", "base"],
    index=1
)

language = st.sidebar.selectbox(
    "Language",
    ["Auto detect", "English"]
)

# Load selected model
@st.cache_resource
def get_model(model_name):
    return whisper.load_model(model_name)

whisper_model = get_model(model_size)

# ---------------------------------------------------------
# AUDIO INPUT
# ---------------------------------------------------------

st.subheader("🎙️ Record your lecture")

audio_value = st.audio_input(
    "Tap the microphone and start recording"
)

# ---------------------------------------------------------
# AUDIO UPLOAD
# ---------------------------------------------------------

st.subheader("📁 Or upload an audio file")

uploaded_audio = st.file_uploader(
    "Upload MP3, WAV, M4A, MP4 or other supported audio",
    type=["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm"]
)

# ---------------------------------------------------------
# CHOOSE AUDIO
# ---------------------------------------------------------

audio_source = audio_value if audio_value else uploaded_audio

if audio_source:

    st.audio(audio_source)

    st.divider()

    if st.button(
        "📝 Transcribe Audio",
        type="primary",
        use_container_width=True
    ):

        temp_path = None

        try:

            with st.spinner("🎧 Transcribing your recording..."):

                # Create temporary audio file
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".wav"
                ) as temp_file:

                    temp_file.write(audio_source.read())
                    temp_path = temp_file.name

                # Transcription options
                options = {}

                if language == "English":
                    options["language"] = "en"

                # Transcribe
                result = whisper_model.transcribe(
                    temp_path,
                    **options
                )

                transcript = result["text"].strip()

            # -------------------------------------------------
            # SAVE TRANSCRIPT IN SESSION
            # -------------------------------------------------

            st.session_state["transcript"] = transcript

            st.success("✅ Transcription completed!")

        except Exception as e:

            st.error(
                "❌ Transcription failed. "
                "Please try the recording again."
            )

            st.exception(e)

        finally:

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)


# ---------------------------------------------------------
# DISPLAY TRANSCRIPT
# ---------------------------------------------------------

if "transcript" in st.session_state:

    transcript = st.session_state["transcript"]

    st.divider()

    st.header("📄 Full Transcript")

    st.text_area(
        "Transcript",
        transcript,
        height=350
    )

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    words = transcript.split()
    word_count = len(words)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Words",
        word_count
    )

    col2.metric(
        "Characters",
        len(transcript)
    )

    reading_time = max(1, round(word_count / 200))

    col3.metric(
        "Reading time",
        f"{reading_time} min"
    )

    # -----------------------------------------------------
    # SIMPLE STUDY SUMMARY
    # -----------------------------------------------------

    st.divider()

    st.header("🧠 Study Summary")

    if word_count < 30:

        summary = (
            "The transcript is too short to create a useful "
            "study summary. Record a longer lecture or upload "
            "a longer audio file."
        )

    else:

        # Split transcript into sentences
        sentences = re.split(
            r'(?<=[.!?])\s+',
            transcript
        )

        sentences = [
            s.strip()
            for s in sentences
            if len(s.strip()) > 20
        ]

        # Simple extractive study summary
        if len(sentences) <= 5:

            selected = sentences

        else:

            # Take important-looking sentences
            keywords = [
                "important",
                "important point",
                "because",
                "therefore",
                "definition",
                "means",
                "example",
                "first",
                "second",
                "third",
                "conclusion",
                "remember"
            ]

            scored = []

            for sentence in sentences:

                score = 0
                lower = sentence.lower()

                for keyword in keywords:

                    if keyword in lower:
                        score += 1

                scored.append(
                    (score, sentence)
                )

            scored.sort(
                key=lambda x: x[0],
                reverse=True
            )

            selected = [
                sentence
                for score, sentence
                in scored[:7]
            ]

        summary = "\n\n".join(
            "• " + sentence
            for sentence in selected
        )

    st.text_area(
        "Important study points",
        summary,
        height=250
    )

    # -----------------------------------------------------
    # DOWNLOAD TRANSCRIPT
    # -----------------------------------------------------

    download_text = f"""
FRANCQUELIN LIVE SCRIBE
=======================

FULL TRANSCRIPT
---------------

{transcript}


STUDY SUMMARY
-------------

{summary}
"""

    st.download_button(
        "📥 Download Transcript + Study Notes",
        download_text,
        file_name="francquelin_live_scribe_notes.txt",
        mime="text/plain",
        use_container_width=True
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="brand">Francquelin Jr™</div>',
    unsafe_allow_html=True
)
