from typing_extensions import TypedDict, Optional
from typing import List
class emailstr(TypedDict,total=False):
    transcription: str
    participants: list[str]
    assign_task: Optional[dict]
    meeting_id: str
    body: str
    subject: str
    to_email: Optional[list]
    emails_payload: Optional[List[dict]]
