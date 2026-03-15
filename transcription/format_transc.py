from fastapi import APIRouter,Request,Depends
from fastapi.responses import StreamingResponse
from auth_service.security import verify_token
from fastapi.responses import JSONResponse
from streaming.stream import generate_rag_stream
from transcription.redis_db import redis_client
from auth_service.schemas import transc_instruction
import json
app=APIRouter()
@app.post("/format_transcription")
async def for_trans(request:Request,payload:transc_instruction,user=Depends(verify_token)):
    try:
        user_id=user["user_id"]
        meeting_id=payload.meeting_id
        instruction=payload.instruction
        key=f"user:{user_id}:meeting:{meeting_id}"
        data=await redis_client.hgetall(key)
        if not data:
            return JSONResponse({"error": "Meeting data not found"}, status_code=404)
        
        raw_transcription=data.get("deep_gram_transcription")
        if not raw_transcription:
            return JSONResponse({"error": "raw_transcription data not found"}, status_code=404)
        transc_graph=request.app.state.transc_graph
        initial_state={
            "raw_transcription":raw_transcription,
            "instruction":instruction
        }
        
        
        async def transcription_event_stream():
             buffer=""
             collected_text = ""
             try:
                 async for chunk in generate_rag_stream(transc_graph,initial_state):
            
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
             finally:
              if collected_text:
                await redis_client.hset(key,mapping={
            "transcription":collected_text
             })
                await redis_client.expire(key,3600)
        return StreamingResponse(
            transcription_event_stream(), media_type="text/event-stream"       )
    
    except Exception as e:
        return JSONResponse({"error": f"{e}"}, status_code=500)



         

