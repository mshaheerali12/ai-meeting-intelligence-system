import streamlit as st
import requests

st.title("🧠 Format Transcription")

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

# ✍️ Instruction input
instruction = st.text_area(
    "Formatting Instruction",
    placeholder="Summarize / bullet points / action items"
)

if st.button("Format"):

    if not instruction:
        st.warning("Please enter instruction")
        st.stop()

    data = {
        "meeting_id": meeting_id,
        "instruction": instruction
    }

    with requests.post(
        "http://127.0.0.1:8000/transcription/format_transcription",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
        stream=True  # 🔥 SAME AS YOUR TRANSCRIPTION
    ) as res:

        if res.status_code != 200:
            st.error(res.text)
            st.stop()

        st.success("Streaming started... 🚀")

        output_box = st.empty()
        full_text = ""

        for chunk in res.iter_lines():
            if chunk:
                decoded = chunk.decode("utf-8")

                # 🔥 Handle SSE format
                if decoded.startswith("data: "):
                    text = decoded.replace("data: ", "").strip()

                    if text == "[DONE]":
                        break

                    full_text += text + " "
                    output_box.markdown(full_text)