from fastapi import APIRouter, Depends, Request,Form
from fastapi.responses import JSONResponse, StreamingResponse
from auth_service.security import verify_token
from nodes.redi import get_retriever
from auth_service.db import get_meeting
from auth_service.schemas import RagQuery, HitlApproval
from streaming.stream import generate_rag_stream
from auth_service.db import get_formatted_meeting,get_meeting,get_recorded_meet,get_v_Trans_meeting
import json
import uuid
import logging
from langsmith import traceable

logger = logging.getLogger(__name__)
app = APIRouter()


@app.post("/ask")
@traceable(name="handle RAG question api")
async def ask_question(
    request: Request,
    meeting_id:str=Form(...),
    question:str=Form(...),
    user=Depends(verify_token)
):
    try:
        user_id = user["user_id"]
        meeting_id =meeting_id
        question =question
        transcription = (
    await get_formatted_meeting(meeting_id)
    or await get_meeting(meeting_id)
    or await get_recorded_meet(meeting_id)
    or await get_v_Trans_meeting(meeting_id)
)

        if not transcription:
            return JSONResponse({"error": "No transcription found"}, status_code=404)
        if isinstance(transcription, dict):
            transcription = transcription.get("data")

        if not isinstance(transcription, str):
            return JSONResponse({"error": "Invalid transcription format"}, status_code=500)

        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        graph_state = {
            "meeting_id": meeting_id,
            "transcription": transcription,
            "question": question,
            "docs": [],
            "web_docs": [],
            "good_docs": [],
            "thread_id": thread_id,
            "user_id": user_id,
        }

       

        graph = request.app.state.rag_graph

        async for _ in graph.astream(graph_state, config=config):
            pass

        snapshot = await graph.aget_state(config)
        if not snapshot or not snapshot.values:
            return JSONResponse({"error": "Session expired or graph did not pause"}, status_code=404)

        full_state = snapshot.values

        if full_state.get("user_id") != user_id:
            return JSONResponse({"error": "Unauthorized"}, status_code=403)

        verdict = full_state.get("verdict", "unknown")
        refined_context = full_state.get("refined_context", "")

        if verdict in ("correct", "ambiguous"):
            async def auto_stream():
                buffer = ""
                try:
                    async for chunk in generate_rag_stream(graph, None, config=config):
                        if chunk.strip() == "data: [DONE]\n\n":
                            if buffer:
                                yield f"data: {json.dumps({'type': 'token', 'content': buffer.strip()})}\n\n"
                            yield "data: [DONE]\n\n"
                            break
                        text = chunk.replace("data: ", "").strip()
                        if not text:
                            continue
                        buffer += f"{text} "
                        if text.endswith((".", "?", ":", ";", "!")):
                            yield f"data: {json.dumps({'type': 'token', 'content': buffer.strip()})}\n\n"
                            buffer = ""
                        elif len(buffer.split()) >= 20:
                            yield f"data: {json.dumps({'type': 'token', 'content': buffer.strip()})}\n\n"
                            buffer = ""
                except Exception as e:
                    logger.error(f"[auto_stream ERROR] {e}", exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Streaming failed'})}\n\n"
                    yield "data: [DONE]\n\n"
            return StreamingResponse(auto_stream(), media_type="text/event-stream")

        return JSONResponse({
            "status": "awaiting_approval",
            "hitl": True,
            "thread_id": thread_id,
            "question": question,
            "verdict": verdict,
            "context_preview": refined_context[:1500] if refined_context else "No context found from web.",
            "message": "No meeting context found — web search was used. Review and call /rag/approve to generate the answer."
        })

    except Exception as e:
        logger.error(f"[/ask ERROR] error={e}", exc_info=True)
        return JSONResponse({"error": "Internal server error"}, status_code=500)


@app.post("/approve")
@traceable(name="approve or reject web search context api")
async def approve_context(
    request: Request,
    payload: HitlApproval,
    user=Depends(verify_token)
):
    try:
        graph = request.app.state.rag_graph
        config = {"configurable": {"thread_id": payload.thread_id}}

        snapshot = await graph.aget_state(config)
        if not snapshot or not snapshot.values:
            return JSONResponse({"error": "No paused session found. It may have expired."}, status_code=404)

        if snapshot.values.get("user_id") != user["user_id"]:
            return JSONResponse({"error": "Unauthorized"}, status_code=403)

        if snapshot.values.get("verdict", "unknown") != "incorrect":
            return JSONResponse({"error": "This session did not require approval."}, status_code=400)

        if not payload.approved:
            return JSONResponse({
                "status": "rejected",
                "message": "Web context rejected. Please rephrase your question and try again.",
                "feedback": payload.feedback or ""
            })

        async def approval_stream():
            buffer = ""
            try:
                async for chunk in generate_rag_stream(graph, None, config=config):
                    if chunk.strip() == "data: [DONE]\n\n":
                        if buffer:
                            yield f"data: {json.dumps({'type': 'token', 'content': buffer.strip()})}\n\n"
                        yield "data: [DONE]\n\n"
                        break
                    text = chunk.replace("data: ", "").strip()
                    if not text:
                        continue
                    buffer += f"{text} "
                    if text.endswith((".", "?", ":", ";", "!")):
                        yield f"data: {json.dumps({'type': 'token', 'content': buffer.strip()})}\n\n"
                        buffer = ""
                    elif len(buffer.split()) >= 20:
                        yield f"data: {json.dumps({'type': 'token', 'content': buffer.strip()})}\n\n"
                        buffer = ""
            except Exception as e:
                logger.error(f"[approval_stream ERROR] {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'content': 'Streaming failed'})}\n\n"
                yield "data: [DONE]\n\n"
        return StreamingResponse(approval_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"[/approve ERROR] error={e}", exc_info=True)
        return JSONResponse({"error": "Internal server error"}, status_code=500)
