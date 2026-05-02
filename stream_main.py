import streamlit as st

st.title("🚀 AI Meeting Assistant")

st.write("Welcome! Use the sidebar to navigate.")

# Optional: show login status
if "token" in st.session_state:
    st.success("✅ Logged in")
else:
    st.warning("⚠️ Not logged in")