import streamlit as st
import requests
from streamlit_mic_recorder import mic_recorder

st.title("🎤 Mic Recorder")
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


audio = mic_recorder(
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    just_once=True,
    use_container_width=True
)

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

if audio and audio != st.session_state.last_audio:
    st.session_state.last_audio = audio

    with st.spinner("Transcribing..."):
      response = requests.post(
        "http://127.0.0.1:8000/pipeline/transcription/record",
        headers={
            "Authorization": f"Bearer {token}"   # ✅ REQUIRED
        },
        data={
            "meeting_id": meeting_id            # ✅ REQUIRED (Form)
        },
        files={
            "file": ("audio.wav", audio["bytes"], "audio/wav")
        }
    )

    data = response.json()

    if "transcript" in data:
     st.success("Done!")
     st.write(data["transcript"])
    else:
        st.error("Something went wrong")
        st.write(data)