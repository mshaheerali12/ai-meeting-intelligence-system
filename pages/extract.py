import streamlit as st
import requests

st.title("📊 Extract Meeting Info")

token = st.session_state.get("token")
meeting_id = st.session_state.get("meeting_id")

if st.button("Extract Info"):

    response = requests.post(
        "http://127.0.0.1:8000/extraction/extract_meeting_info",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"meeting_id": meeting_id},
        stream=True   # ✅ IMPORTANT
    )

    output = ""
    placeholder = st.empty()

    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")

            if decoded.strip() == "data: [DONE]":
                break

            if decoded.startswith("data: "):
                text = decoded.replace("data: ", "").strip()
                output += text + " "
                placeholder.markdown(output)