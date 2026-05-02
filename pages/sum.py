import streamlit as st
import requests

st.title("📄 Meeting Summary")

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

if st.button("Generate Summary"):

    data = {
        "meeting_id": meeting_id
    }

    res = requests.post(
        "http://127.0.0.1:8000/summary/summary",
        headers={"Authorization": f"Bearer {token}"},
        data=data
    )

    if res.status_code != 200:
        st.error(res.text)
        st.stop()

    result = res.json()
    summary = result.get("summary", "")

    st.subheader("🧾 Summary")
    st.markdown(summary)