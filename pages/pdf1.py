import streamlit as st
import requests

st.title("📄 Meeting PDF Generator")

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

# 🚀 Generate PDF
if st.button("Generate PDF"):

    data = {
        "meeting_id": meeting_id
    }

    res = requests.post(
        "http://127.0.0.1:8000/pdf/generate_pdf",
        headers={"Authorization": f"Bearer {token}"},
        data=data
    )

    # ❌ Error handling
    if res.status_code != 200:
        st.error(res.text)
        st.stop()

    # 📄 PDF bytes from StreamingResponse
    pdf_bytes = res.content

    st.success("PDF generated successfully!")

    # ⬇️ Download button
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_bytes,
        file_name=f"meeting_{meeting_id}.pdf",
        mime="application/pdf"
    )

    # 👀 Optional preview
    st.write("Preview:")
    st.pdf(pdf_bytes)