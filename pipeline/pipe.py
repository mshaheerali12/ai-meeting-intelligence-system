from fastapi import APIRouter, Depends, Request, UploadFile, File,Form
from fastapi.responses import JSONResponse,StreamingResponse
from auth_service.security import verify_token
from auth_service.db import cache_meeting
from deepgram import AsyncDeepgramClient
from streaming.stream import generate_rag_stream
from auth_service.db import cache_meeting
from auth_service.database import collection2
from nodes.redi import get_retriever

import httpx
import uuid
import json
import os
import logging

logger = logging.getLogger(__name__)
app = APIRouter()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")



# AsyncDeepgramClient with long read timeout for large files
dg_client = AsyncDeepgramClient(
    api_key=DEEPGRAM_API_KEY,
    timeout=httpx.Timeout(connect=30.0, read=600.0, write=300.0, pool=30.0)
)


@app.post("/transcription/raw")
async def rws(
    request: Request,
    meeting_id: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(verify_token)
):
    try:
        
        audio = await file.read()

        if not audio:
            return JSONResponse({"error": "Uploaded file is empty."}, status_code=400)

        key = meeting_id
        user_id=user["user_id"]
        db=await collection2.find_one({"id":key})
        participants=db.get("participants",[]) if db else []
        

        # Capture graph before entering generator
      
        res=await dg_client.listen.v1.media.transcribe_file(
        request=audio,
        model="nova-2",
        language="en-US",
        punctuate=True,
        diarize=True
    )
        speaker_map = {
        int(p["speaker"]): {
        "name": p["name"],
        "role": p["role"],
    }
    for p in participants
}

        words = res.results.channels[0].alternatives[0].words

        lines = []
        current_speaker = None
        current_sentence = []

        for w in words:
         speaker = int(w.speaker or 0)
         word = w.word or ""

         if speaker != current_speaker:
            if current_sentence:
             sp = speaker_map.get(current_speaker, {})
             name = sp.get("name", f"Speaker {current_speaker}")
             role = f" ({sp.get('role')})" if sp.get("role") else ""
             lines.append(f"{name}{role}: {' '.join(current_sentence)}")

            current_sentence = [word]
            current_speaker = speaker
         else:
            current_sentence.append(word)

        if current_sentence:
            sp = speaker_map.get(current_speaker, {})
            name = sp.get("name", f"Speaker {current_speaker}")
            role = f" ({sp.get('role')})" if sp.get("role") else ""
            lines.append(f"{name}{role}: {' '.join(current_sentence)}")

        final_transcript = "\n".join(lines)
        await get_retriever(final_transcript,key)
        await cache_meeting(key, final_transcript)
   
        return {
    
    "transcript": final_transcript
}
    except Exception as e:
        logger.error(f"[pipe] Error processing transcription: {e}", exc_info=True)
        return JSONResponse({"error": "Failed to process transcription"}, status_code=500)