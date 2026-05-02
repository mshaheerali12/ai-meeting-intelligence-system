import requests
import streamlit as st

st.title("Signup")

with st.form("signup_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    submit = st.form_submit_button("Sign Up")

    if submit:
        data = {
            "name": name,
            "email": email,
            "password": password
        }

        res = requests.post("http://127.0.0.1:8000/auth/register", json=data)

        if res.status_code == 200:
            st.success("Signup successful 🎉")
        else:
            st.error("Something went wrong")