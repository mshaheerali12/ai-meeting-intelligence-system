from typing_extensions import TypedDict, Optional
from langchain_core.documents import Document


class meemory(TypedDict):
    meeting_id: str
    question: str
    docs: list[Document]
    strips: list[Document]
    kept_strips: list[Document]
    refined_context: Optional[str]
    answer: str
    good_docs: list[Document]
    verdict: Optional[str]
    reason: Optional[str]
    web_docs: list[Document]
    web_query: Optional[str]
    final_transcription: Optional[str]

    audio_bytes: Optional[bytes]
    pdf_bytes: Optional[bytes]
    raw_transcription: Optional[str]
    instruction: Optional[str]
    transcription: str
    summary: Optional[str]
    speaker_map: Optional[dict[str, dict[str, str]]]

    # HITL fields
    hitl_approved: Optional[bool]
    hitl_feedback: Optional[str]
    thread_id: Optional[str]
    meet_res:dict[list]
    # Auth — must be in state so checkpointer saves and restores it
    user_id: Optional[str]
