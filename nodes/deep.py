from deepgram import  AsyncDeepgramClient
import httpx
import logging
from io import BytesIO
from nodes.state import meemory

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",filename="transciption.log",filemode="w")
logger = logging.getLogger(__name__)
try:
 client = AsyncDeepgramClient(api_key="68927c6f0bdf7975cd8b490ab461ec102dab36c7",timeout=httpx.Timeout(2400.0))
except Exception as e:
    logger.error(f"Failed to initialize Deepgram client: {e}")
    raise

async def transcribe(state:meemory):
   try:
        logger.info("Starting transcription request to Deepgram")

        if "audio_bytes" not in state:
            raise ValueError("Missing 'audio_bytes' in state")
        audio_bytes=state["audio_bytes"]
        
        response = await client.listen.v1.media.transcribe_file(
             
        request= audio_bytes,
        model= "nova-3",
        punctuate= True
    
        )

        transcript = (
            response.results.channels[0]
            .alternatives[0]
            .transcript
        )

        if not transcript:
            raise ValueError("Deepgram returned empty transcript")

        logger.info("Transcription completed successfully")

        return {"raw_transcription": transcript}

   except httpx.TimeoutException:
        logger.error("Deepgram request timed out", exc_info=True)
        raise

   except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        raise