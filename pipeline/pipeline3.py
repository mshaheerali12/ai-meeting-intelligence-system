from fastapi import APIRouter,Depends,UploadFile,File,Form
from fastapi.responses import JSONResponse
from deepgram import AsyncDeepgramClient
from auth_service.security import verify_token
from auth_service.database import collection2
from nodes.redi import get_retriever
from auth_service.db import recorded_meet
from dotenv import load_dotenv
import os
load_dotenv()
api_key=os.getenv("DEEPGRAM_API_KEY")
client=AsyncDeepgramClient(api_key=api_key)
app=APIRouter()
@app.post("/transcription/record")
async def recorder_mic(meeting_id:str=Form(...),file:UploadFile=File(...),user=Depends(verify_token)):
    audio_bytes=await file.read()
    user_id=user["user_id"]
    db=await collection2.find_one({"id":meeting_id})
    participants=db.get("participants",[]) if db else []
    try:
        res=await client.listen.v1.media.transcribe_file(
        request=audio_bytes,
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
        await get_retriever(final_transcript,meeting_id)
        await recorded_meet(meeting_id, final_transcript)
   
        return {
    
    "transcript": final_transcript
}
    except Exception as e:
        return JSONResponse({"error": "Failed to process transcription"}, status_code=500)
