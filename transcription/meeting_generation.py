from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from auth_service.schemas import Meeting
from auth_service.security import verify_token
from auth_service.database import collection2
import uuid
import logging

logger = logging.getLogger(__name__)
app = APIRouter()


@app.post("/meeting_generation")
async def meet_gen(payload: Meeting, user=Depends(verify_token)):
    try:
        user_id = user["user_id"]
        strid = str(uuid.uuid4())
        key = f"user_id:{user_id}:meeting:{strid}"

        meet = {
            "id": key,
            "agenda": payload.agenda,
            "date": payload.date,
            "participants": [p.dict() for p in payload.participants]
        }

        # Insert a COPY — MongoDB mutates the original dict by injecting
        # "_id": ObjectId(...) after insert_one, which breaks JSON serialization
        result = await collection2.insert_one(meet.copy())

        logger.info(f"Meeting profile created: meeting_id={key} user_id={user_id}")

        return {
            "meeting_id": key,
            "mongo_id": str(result.inserted_id),
            # Return the original meet dict — no ObjectId inside
            "meeting_details": meet
        }

    except Exception as e:
        logger.error(f"[meet_gen ERROR] user_id={user.get('user_id')} error={e}", exc_info=True)
        return JSONResponse({"error": "Failed to create meeting profile."}, status_code=500)
