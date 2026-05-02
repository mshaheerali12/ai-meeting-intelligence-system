import streamlit as st
import requests
st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    res = requests.post("http://127.0.0.1:8000/auth/login", json={"email": email, "password": password})
    # call FastAPI API
    if res.status_code == 200:
       data = res.json()
       token = data.get("token")

       if not token:
        st.error("Token missing in response")
        st.stop()
       st.session_state["token"] = token
       st.session_state["logged_in"] = True

       st.success("Logged in")
       st.rerun()
    else:
        st.error("Invalid credentials")