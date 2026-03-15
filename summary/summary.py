from fastapi import APIRouter,Depends,Request
from auth_service.security import verify_token
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from transcription.redis_db import redis_client
from auth_service.schemas import summary_response
from streaming.stream import generate_rag_stream
import json

app=APIRouter()
@app.post("/summary" )
async def generate_summary(request:Request,payload:summary_response,user=Depends(verify_token)):
   try:
      
      user_id=user["user_id"]
      meeting_id=payload.meeting_id
      key=f"user:{user_id}:meeting:{meeting_id}"
      data=await redis_client.hgetall(key)
      sum_graph=request.app.state.sum_graph
      if not data:
        return JSONResponse({"error": "Meeting data not found"}, status_code=404)
      
      transcription=data.get("transcription")
      if not transcription:
            return JSONResponse({"error": "Transcription data not found"}, status_code=404)
      initial_state={"transcription":transcription}
      async def summary_stream_event():
          buffer=""
          collected_text = ""
          try:
            async for chunk in generate_rag_stream(sum_graph,initial_state):
            
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
            "summary":collected_text
             })
                await redis_client.expire(key,3600)
      return StreamingResponse(
            summary_stream_event(), media_type="text/event-stream"       )
   except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
