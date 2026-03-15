from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse,StreamingResponse
from auth_service.security import verify_token
from nodes.pdf_gen import generate_meeting_pdf_bytes
from transcription.redis_db import redis_client
from auth_service.schemas import summary_response
import io

app=APIRouter()
@app.post("/generate_pdf")
async def gent_pdf(request:summary_response,user=Depends(verify_token)):
    try:
       user_id=user["user_id"]
       meeting_id=request.meeting_id
       key=f"user:{user_id}:meeting:{meeting_id}"
       data=await redis_client.hgetall(key) 
       if not data:
        return JSONResponse({"error": "Meeting data not found"}, status_code=404)
       transcription=data.get("transcription")
       summary=data.get("summary")
       if not transcription or not summary:
            return JSONResponse({"error": "Transcription or summary data not found"}, status_code=404)
       pdf_bytes=generate_meeting_pdf_bytes(transcription,summary)
       return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.pdf"})
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
       