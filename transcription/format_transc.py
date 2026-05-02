from fastapi import APIRouter, Request, Depends,Form
from fastapi.responses import StreamingResponse, JSONResponse
from auth_service.security import verify_token
from streaming.stream import generate_rag_stream
from auth_service.db import  get_meeting,format_meeting,get_v_Trans_meeting,get_recorded_meet
from auth_service.schemas import transc_instruction
from langsmith import traceable
import json
import logging

logger = logging.getLogger(__name__)
app = APIRouter()


@app.post("/format_transcription")
@traceable(name="format meeting transcription api")
async def for_trans(request: Request,instruction: str = Form(...), meeting_id:str=Form(...), user=Depends(verify_token)):
    try:
        user_id = user["user_id"]
        meeting_id = meeting_id
        instruction = instruction
        key = meeting_id

        data = await get_meeting(key) or get_v_Trans_meeting(key) or await get_recorded_meet(key)
        if not data:
            return JSONResponse({"error": "meeting didnt provided"})
            

      

        transc_graph = request.app.state.transc_graph
        initial_state = {
            "raw_transcription": data,
            "instruction": instruction
        }

        async def transcription_event_stream():
            buffer = ""
            collected_text = ""
            try:
                async for chunk in generate_rag_stream(transc_graph, initial_state):
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
                logger.error(f"[format stream ERROR] meeting_id={meeting_id} error={e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'content': 'Formatting failed'})}\n\n"
                yield "data: [DONE]\n\n"

            finally:
                if collected_text:
                    try:
                        await format_meeting(key, collected_text)
                        logger.info(f"[format] Saved to MongoDB: meeting_id={meeting_id}")
                    except Exception as e:
                        logger.error(f"[format save ERROR] meeting_id={meeting_id} error={e}", exc_info=True)

        return StreamingResponse(transcription_event_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"[format ERROR] meeting_id={meeting_id} error={e}", exc_info=True)
        return JSONResponse({"error": "Internal server error during transcription formatting."}, status_code=500)
