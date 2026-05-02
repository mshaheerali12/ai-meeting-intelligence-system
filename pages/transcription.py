import streamlit as st
import requests

st.title("🎙️ Transcription")

# 🔐 Auth check
token = st.session_state.get("token")
if not token:
    st.error("Please login first")
    st.stop()

# 📌 Get meeting_id
meeting_id = st.session_state.get("meeting_id")

if not meeting_id:
    st.warning("No meeting selected. Create a meeting first.")
    st.stop()

st.success(f"Using Meeting ID: {meeting_id}")

# 🎧 Upload file
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])

if st.button("Transcribe"):
    if not audio_file:
        st.warning("Upload a file first")
        st.stop()

    files = {
        "file": (audio_file.name, audio_file, audio_file.type)
    }

    data = {
        "meeting_id": meeting_id
    }

    with requests.post(
    "http://127.0.0.1:8000/pipeline/transcription/raw",
    headers={"Authorization": f"Bearer {token}"},
    files=files,
    data=data,
    stream=True  # 🔥 IMPORTANT
) as res:

     if res.status_code != 200:
        st.error(res.text)
        st.stop()

     st.success("Streaming started... 🚀")

     output_box = st.empty()
     full_text = ""

     for chunk in res.iter_lines():
        if chunk:
            text = chunk.decode("utf-8")

            full_text += text + " "
            output_box.markdown(full_text)