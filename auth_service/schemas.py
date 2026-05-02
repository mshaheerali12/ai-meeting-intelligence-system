from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegistration(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr


class login_user(BaseModel):
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class summary_response(BaseModel):
    meeting_id: str


class RagQuery(BaseModel):
    meeting_id: str
    question: str


class transc_instruction(BaseModel):
    instruction: str


# HITL schemas
class HitlApproval(BaseModel):
    thread_id: str           # the paused graph's thread ID
    approved: bool           # True = continue to generate, False = reject
    feedback: Optional[str] = None   # optional note if rejected

class Participant(BaseModel):
    speaker: int
    name: str
    email: EmailStr
    role: str

class Meeting(BaseModel):
    agenda: str
    date: str
    participants: list[Participant]