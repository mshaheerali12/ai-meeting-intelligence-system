from fastapi import APIRouter,Depends,UploadFile,File,Form
from fastapi.responses import JSONResponse
from deepgram import AsyncDeepgramClient
import subprocess
from auth_service.database import collection2
from auth_service.db import v_transc_meeting 
from auth_service.security import verify_token
from nodes.redi import get_retriever
from dotenv import load_dotenv
import os
load_dotenv()
api_key=os.getenv("DEEPGRAM_API_KEY")
client=AsyncDeepgramClient(api_key=api_key,timeout=None)
app=APIRouter()
async def video_to_audio_bytes(video_bytes: bytes) -> bytes:
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-i", "pipe:0",
            "-f", "wav",
            "-ac", "1",
            "-ar", "16000",
            "-vn",
            "pipe:1"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    audio_bytes, err = process.communicate(input=video_bytes)

    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {err.decode()}")

    return audio_bytes
@app.post("/transcription/video")
async def videotran(meeting_id:str=Form(...),file:UploadFile=File(...),user=Depends(verify_token)):
    key=meeting_id
    user_id=user["user_id"]
    db=await collection2.find_one({"id":key})
    participants=db.get("participants",[]) if db else []
    v_bytes=await file.read()
    if not v_bytes:
       return JSONResponse({"error":"file didn't recognized"})
    v_audio=await video_to_audio_bytes(v_bytes)
    try:
        res=await client.listen.v1.media.transcribe_file(
        request=v_audio,
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
        await v_transc_meeting(key, final_transcript)
   
        return {
    
    "transcript": final_transcript
}
    except Exception as e:
        return JSONResponse({"error": "Failed to process transcription"}, status_code=500)
