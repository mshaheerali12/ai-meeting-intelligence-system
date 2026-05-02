from auth_service.security import verify_token
from fastapi import APIRouter, Depends, Request,Form
from fastapi.responses import JSONResponse, StreamingResponse
from auth_service.db import get_meeting,get_formatted_meeting,get_v_Trans_meeting,get_recorded_meet
from langsmith import traceable
from streaming.stream import generate_rag_stream
from auth_service.schemas import summary_response
import json
import logging

logger = logging.getLogger(__name__)
app = APIRouter()


@app.post("/extract_meeting_info")
@traceable(name="extract meeting info api")
async def extract_info(request: Request, meeting_id: str = Form(...), user=Depends(verify_token)):
    try:
        user_id = user["user_id"]
        meeting_id = meeting_id
        key = meeting_id

        if key:
            data = await get_formatted_meeting(key) or await get_meeting(key) or await get_v_Trans_meeting(key) or get_recorded_meet(key)
        else:
            return JSONResponse({"error": "Meeting ID is required"}, status_code=400)

      

        graph = request.app.state.ext_graph
        initial_state = {"transcription": data}

        async def ext_event_stream():
            buffer = ""
            collected_text = ""
            try:
                async for chunk in generate_rag_stream(graph, initial_state):
                    if chunk.strip() == "data: [DONE]\n\n":
                        if buffer:
                            yield f"data: {buffer.strip()}\n\n"
                        yield "data: [DONE]\n\n"
                        break

                    text = chunk.replace("data: ", "").strip()
                    if not text:
                        continue

                    buffer += f"{text} "
                    collected_text += f"{text} "

                    if text.endswith((".", "?", ":", ";", "!")):
                        yield f"data: {buffer.strip()}\n\n"
                        buffer = ""
                    elif len(buffer.split()) >= 20:
                        yield f"data: {buffer.strip()}\n\n"
                        buffer = ""

            except Exception as e:
                logger.error(f"[extract stream ERROR] meeting_id={meeting_id} error={e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'content': 'Extraction failed'})}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(ext_event_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"[extract ERROR] meeting_id={meeting_id} error={e}", exc_info=True)
        return JSONResponse({"error": "Internal server error during extraction."}, status_code=500)
