import streamlit as st
import requests

st.title("🧠 RAG Question Answering")

# 🔐 Auth check
token = st.session_state.get("token")
if not token:
    st.error("Please login first")
    st.stop()

# 📌 Meeting ID
meeting_id = st.session_state.get("meeting_id")
if not meeting_id:
    st.warning("No meeting selected. Create/select a meeting first.")
    st.stop()

st.success(f"Using Meeting ID: {meeting_id}")

# ✍️ Question input
question = st.text_area(
    "Ask your question",
    placeholder="e.g. What are the key decisions in this meeting?"
)

if st.button("Ask"):

    if not question:
        st.warning("Please enter a question")
        st.stop()

    data = {
        "meeting_id": meeting_id,
        "question": question
    }

    with requests.post(
        "http://127.0.0.1:8000/rag/ask",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
        stream=True
    ) as res:

        # ---------------------------
        # CASE 1: HITL RESPONSE
        # ---------------------------
        try:
            if res.headers.get("content-type", "").startswith("application/json"):
                result = res.json()

                if result.get("status") == "awaiting_approval":
                    st.warning("⚠️ Web search context detected. Approval required.")

                    st.json({
                        "thread_id": result["thread_id"],
                        "verdict": result["verdict"],
                        "preview": result["context_preview"]
                    })

                    thread_id = result["thread_id"]

                    approve = st.radio("Approve web context?", ["Yes", "No"])

                    feedback = st.text_input("Feedback (optional)")

                    if st.button("Submit Approval"):

                        payload = {
                            "thread_id": thread_id,
                            "approved": approve == "Yes",
                            "feedback": feedback
                        }

                        with requests.post(
                            "http://127.0.0.1:8000/rag/approve",
                            headers={"Authorization": f"Bearer {token}"},
                            json=payload,
                            stream=True
                        ) as approve_res:

                            if approve_res.status_code != 200:
                                st.error(approve_res.text)
                                st.stop()

                            st.success("Streaming final answer... 🚀")

                            output_box = st.empty()
                            full_text = ""

                            for chunk in approve_res.iter_lines():
                                if chunk:
                                    decoded = chunk.decode("utf-8")

                                    if decoded.startswith("data: "):
                                        text = decoded.replace("data: ", "").strip()

                                        if text == "[DONE]":
                                            break

                                        try:
                                            import json
                                            data = json.loads(text)
                                            if data.get("type") == "token":
                                                full_text += data["content"] + " "
                                                output_box.markdown(full_text)
                                        except:
                                            full_text += text + " "
                                            output_box.markdown(full_text)

                    st.stop()

        except:
            pass

        # ---------------------------
        # CASE 2: NORMAL STREAMING
        # ---------------------------
        st.success("Streaming answer... 🚀")

        output_box = st.empty()
        full_text = ""

        for chunk in res.iter_lines():
            if chunk:
                decoded = chunk.decode("utf-8")

                if decoded.startswith("data: "):
                    text = decoded.replace("data: ", "").strip()

                    if text == "[DONE]":
                        break

                    try:
                        import json
                        data = json.loads(text)

                        if data.get("type") == "token":
                            full_text += data["content"] + " "
                            output_box.markdown(full_text)

                    except:
                        full_text += text + " "
                        output_box.markdown(full_text)