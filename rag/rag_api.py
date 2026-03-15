from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse,StreamingResponse
from langchain_core.messages import AIMessageChunk
from fastapi.staticfiles import StaticFiles
from auth_service.security import verify_token
from nodes import state
import json
from nodes.redi import get_retriever
from transcription.redis_db import redis_client
from auth_service.schemas import RagQuery
from streaming.stream import generate_rag_stream

app = APIRouter()

@app.post("/ask")
async def ask_question(
    request: Request,
    data: RagQuery,
    user=Depends(verify_token)
):
    print("REQUEST RECEIVED:", data.question)
    try:

        user_id = user["user_id"]
        meeting_id = data.meeting_id
        question = data.question

        # verify meeting belongs to user
        key = f"user:{user_id}:meeting:{meeting_id}"
        print("REDIS KEY:", key)
        meeting_data = await redis_client.hgetall(key)
        print("REDIS DATA:", meeting_data)

        if not meeting_data:
            return JSONResponse(
                {"error": "Meeting not found"},
                status_code=404
            )

        transcription = meeting_data.get("transcription")

        if not transcription:
            return JSONResponse(
                {"error": "Transcription missing"},
                status_code=404
            )

        # LangGraph state
        graph_state = {
            "meeting_id": meeting_id,
            "transcription": transcription,
            "question": question,
            "docs": [],
            "web_docs": [],
            "good_docs": []
        }

        retriever_state = await get_retriever(transcription,meeting_id)
        graph_state.update(retriever_state)
        # run RAG graph
        graph = request.app.state.rag_graph
        async def rag_event_stream():
            buffer=""
            collected_text = ""
            
            async for chunk in generate_rag_stream(graph,graph_state):
            
                    if chunk.strip() == "data: [DONE]\n\n":
                       if buffer:
                            yield f"data: {json.dumps({'type':'token','content':buffer.strip()})}\n\n"
                       yield "data: [DONE]\n\n"
                       break

                    text = chunk.replace("data: ", "").strip()
                    if not text:
                        continue
                    buffer +=f"{text} "
                    collected_text +=f"{text} "
                    if text.endswith( (".","?",":",";","!")):
                       yield f"data: {json.dumps({'type':'token','content':buffer.strip()})}\n\n"
                       buffer = ""
                    else:
                      if len(buffer.split()) >= 20:
                        yield f"data: {json.dumps({'type':'token','content':buffer.strip()})}\n\n"
                        buffer = ""
                       
        return StreamingResponse(
            rag_event_stream(), media_type="text/event-stream"       )


    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
