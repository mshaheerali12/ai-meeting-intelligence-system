from typing_extensions import TypedDict,Optional
from langchain_core.documents import Document
class meemory(TypedDict):
    meeting_id:str
    question:str
    docs:list[Document]
    strips:list[Document]
    kept_strips:list[Document]
    refined_context:Optional[str]
    answer:str
    good_docs:list[Document]
    verdict:Optional[str]
    reason:Optional[str]
    web_docs:list[Document]
    web_query:Optional[str]
    

    audio_bytes:Optional[bytes]

    pdf_bytes:Optional[bytes]

    raw_transcription:Optional[str]

    instruction:Optional[str]
    transcription:str
    summary:Optional[str]

    
