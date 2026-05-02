from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client["user_registration"]
collection0=db["token_blacklist"]
collection1 = db["users"]
collection2=db["meetings"]
collection3=db["Transcriptions"]
collection4=db["format_transcriptions"]
collection5=db["summaries"]
collection6=db["extractions"]
collection7=db["video_transcription"]
collection8=db["recording"]
collection9=db["rag_check"]