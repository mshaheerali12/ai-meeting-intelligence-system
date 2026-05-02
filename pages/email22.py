import streamlit as st
import requests

st.title("📧 Auto Email Generator")

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

# 🚀 Trigger emails
if st.button("Send Auto Emails"):

    data = {
        "meeting_id": meeting_id
    }

    with st.spinner("Generating emails and sending..."):

        res = requests.post(
            "http://127.0.0.1:8000/meeting_gen/automails",
            headers={"Authorization": f"Bearer {token}"},
            data=data
        )

    # ❌ Error handling
    if res.status_code != 200:
        st.error("Failed to send emails")
        st.write(res.text)
        st.stop()

    result = res.json()

    st.success(result.get("message", "Done"))

    # Optional debug (very useful)
    st.write("Response:")
    st.json(result)