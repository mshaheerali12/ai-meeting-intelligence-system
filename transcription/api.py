from fastapi import APIRouter,UploadFile,Request,File,Form,Depends
from fastapi.responses import StreamingResponse
from auth_service.security import verify_token
from fastapi.responses import JSONResponse
from streaming.stream import generate_rag_stream
from transcription.redis_db import redis_client
import uuid
import json
app=APIRouter()

@app.post("/upload_file")
async def trnscription(request:Request,file:UploadFile=File(...),user=Depends(verify_token)):
    try:
        audio_bytes=await file.read()
        
        app_graph=request.app.state.app_graph
        user_id=user["user_id"]
        meeting_id = str(uuid.uuid4())  
        key=f"user:{user_id}:meeting:{meeting_id}"
        ini_state={
            "audio_bytes":audio_bytes,
            "instruction":None
        }
        result = await app_graph.ainvoke(ini_state)
        async def deepgram_event_stream():
             yield f"data: {json.dumps({'meeting_id':meeting_id})}\n\n"
             buffer=""
             collected_text = ""
             try:
                 async for chunk in generate_rag_stream(app_graph,ini_state):
            
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
            "raw_transcription":collected_text
             })
                await redis_client.expire(key,3600)
        return StreamingResponse(
            deepgram_event_stream(), media_type="text/event-stream"       )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)




