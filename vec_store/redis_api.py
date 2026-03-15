from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import JSONResponse
from auth_service.security import verify_token
from nodes.redi import get_retriever
from transcription.redis_db import redis_client
from auth_service.schemas import summary_response

app=APIRouter()
@app.post("/vector_store")
async def vector_store(request:summary_response,user=Depends(verify_token)):
    try:
        user_id=user["user_id"]
        meeting_id=request.meeting_id
        key=f"user:{user_id}:meeting:{meeting_id}"
        data=await redis_client.hgetall(key)
        if not data: 
         return JSONResponse({"error": "Meeting data not found"}, status_code=404)
        transcription=data.get("transcription")
        if not transcription:
            return JSONResponse({"error": "Transcription not found"}, status_code=404)
    
             
    
        retriever=await get_retriever(transcription,meeting_id )
        return {"message": "Vector store created successfully","meeting_id": meeting_id}
    except Exception as e:
       return JSONResponse(
            {"error": str(e)},
            status_code=500
        )

       