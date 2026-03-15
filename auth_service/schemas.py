from pydantic import BaseModel, EmailStr, Field
class UserRegistration(BaseModel):
    name:str= Field(..., min_length=3, max_length=50)
    email:EmailStr= Field(..., max_length=100)
    password:str= Field(..., min_length=6, max_length=100)
class UserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
class login_user(BaseModel):
    email:EmailStr= Field(..., max_length=100)
    password:str= Field(..., min_length=6, max_length=100)
class summary_response(BaseModel):
    meeting_id:str
class RagQuery(BaseModel):
    meeting_id:str
    question:str
class transc_instruction(BaseModel):
    meeting_id:str
    instruction:str
    
  