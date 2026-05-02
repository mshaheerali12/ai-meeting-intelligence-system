import streamlit as st
import requests

st.title("📅 Create Meeting")

# 🔐 AUTH CHECK FIRST
token = st.session_state.get("token")

if not token:
    st.error("Please login first")
    st.stop()

agenda = st.text_input("Agenda")
date = st.date_input("Date")

# INIT
if "participants" not in st.session_state:
    st.session_state.participants = 1

st.subheader("Participants")

participants_data = []

for i in range(st.session_state.participants):

    st.markdown(f"### Speaker {i+1}")

    name = st.text_input(f"Name {i}", key=f"name_{i}")
    email = st.text_input(f"Email {i}", key=f"email_{i}")
    role = st.text_input(f"Role {i}", key=f"role_{i}")

    participants_data.append({
        "speaker": i ,
        "name": name,
        "email": email,
        "role": role
    })

# ➕ Add participant
if st.button("➕ Add Participant"):
    st.session_state.participants += 1
    st.rerun()

# 🚀 Submit
if st.button("Submit Meeting"):

    data = {
        "agenda": agenda,
        "date": str(date),
        "participants": participants_data
    }

    st.write("📦 Sending Data:", data)

    res = requests.post(
        "http://127.0.0.1:8000/meeting_gen/meeting_generation",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    if res.status_code == 200:
        response_data = res.json()

        meeting_id = response_data.get("meeting_id")

        if not meeting_id:
            st.error("No meeting_id returned from server")
            st.stop()

    # 🔥 SAVE IT HERE
    st.session_state["meeting_id"] = meeting_id

    st.success("Meeting created 🎉")
    st.code(meeting_id)

    # Debug (optional)
    st.write("Stored meeting_id:", st.session_state.get("meeting_id"))
 