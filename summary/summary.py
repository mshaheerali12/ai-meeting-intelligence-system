from fastapi import APIRouter, Depends, Request,Form
from fastapi.responses import JSONResponse, StreamingResponse
from auth_service.security import verify_token
from nodes.redi import get_retriever
from auth_service.db import  get_meeting,get_formatted_meeting,get_v_Trans_meeting,get_recorded_meet
from auth_service.schemas import summary_response
from auth_service.db import summary_meet
from streaming.stream import generate_rag_stream
import json
import logging
from langsmith import traceable

logger = logging.getLogger(__name__)
app = APIRouter()


@app.post("/summary")
@traceable(name="generate meeting summary api")
async def generate_summary(request: Request, meeting_id:str=Form(...), user=Depends(verify_token)):
    try:
        user_id = user["user_id"]
        meeting_id = meeting_id
        key = meeting_id
        
        sum_graph = request.app.state.sum_graph

        transcription=await get_meeting(key) or  await get_formatted_meeting(key) or await get_v_Trans_meeting(key) or await get_recorded_meet(key)
        if not transcription:
            return JSONResponse({"error": "No transcription found for the given meeting_id."}, status_code=404)
        
    
        initial_state = {"transcription": transcription}
        output=""

        async for chunk in generate_rag_stream(sum_graph, initial_state):
            if chunk: 
             output+=chunk.strip() + " "
        await summary_meet(key,output.strip())
        return {"summary": output.strip()}

    except Exception as e:
        logger.error(f"[Summary ERROR] meeting_id={meeting_id} error={e}", exc_info=True)
        return JSONResponse({"error": "Internal server error during summary generation."}, status_code=500)
