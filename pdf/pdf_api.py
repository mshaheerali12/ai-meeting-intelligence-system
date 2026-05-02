from fastapi import APIRouter, Depends,Form
from fastapi.responses import JSONResponse, StreamingResponse
from auth_service.security import verify_token
from nodes.pdf_gen import generate_meeting_pdf_bytes
from auth_service.db import get_summary_meet
from auth_service.schemas import summary_response
from langsmith import traceable
import logging
import io

logger = logging.getLogger(__name__)
app = APIRouter()


@app.post("/generate_pdf")
@traceable(name="generate meeting PDF api")
async def generate_pdf( meeting_id:str=Form(...), user=Depends(verify_token)):
    try:
        user_id = user["user_id"]
        meeting_id = meeting_id
        

        data = await get_summary_meet(meeting_id)
        if not data:
            return JSONResponse({"error": "Meeting data not found"}, status_code=404)

        summary_text = data.get("data")
       

        try:
            pdf_bytes = await generate_meeting_pdf_bytes(summary_text)
        except Exception as e:
            logger.error(f"[PDF generation ERROR] meeting_id={meeting_id} error={e}", exc_info=True)
            return JSONResponse({"error": "Failed to generate PDF."}, status_code=500)

        logger.info(f"PDF generated: meeting_id={meeting_id} size={len(pdf_bytes)} bytes")
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.pdf"}
        )

    except Exception as e:
        logger.error(f"[PDF ERROR] meeting_id={meeting_id} error={e}", exc_info=True)
        return JSONResponse({"error": "Internal server error during PDF generation."}, status_code=500)
