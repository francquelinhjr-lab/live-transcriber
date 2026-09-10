import streamlit as st
import whisper
from transformers import pipeline
import tempfile

st.set_page_config(page_title="Live Transcriber + Summarizer", page_icon="🎙️")

@st.cache_resource
def load_models():
    whisper_model = whisper.load_model("tiny")
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return whisper_model, summarizer

whisper_model, summarizer = load_models()

st.title("🎙️ Live Transcriber + Summarizer")
st.write("Record audio using your microphone, then get a transcript and summary — free, no login required.")

audio_value = st.audio_input("Record your audio")

if audio_value:
    with st.spinner("Transcribing..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_value.read())
            tmp_path = tmp.name

        result = whisper_model.transcribe(tmp_path)
        transcript = result["text"].strip()

    st.subheader("Full Transcript")
    st.text_area("Transcript", transcript, height=200, label_visibility="collapsed")

    word_count = len(transcript.split())
    if word_count > 30:
        with st.spinner("Summarizing..."):
            summary = summarizer(transcript, max_length=100, min_length=20, do_sample=False)
            summary_text = summary[0]["summary_text"]
    else:
        summary_text = "Recording too short to summarize (needs 30+ words)."

    st.subheader("Summary")
    st.text_area("Summary", summary_text, height=150, label_visibility="collapsed")

    file_content = f"TRANSCRIPT:\n{transcript}\n\nSUMMARY:\n{summary_text}"
    st.download_button(
        label="Download Transcript + Summary (.txt)",
        data=file_content,
        file_name="transcript_summary.txt",
        mime="text/plain"
)
