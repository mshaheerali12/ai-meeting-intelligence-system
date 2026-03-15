from fastapi import APIRouter, HTTPException,status,Request,Depends
from auth_service.database import collection
from auth_service.schemas import UserRegistration,login_user,UserResponse
from auth_service.security import create_access_token,verify_token,get_current_user
from datetime import datetime,timedelta
from transcription.redis_db import redis_client
from pwdlib import PasswordHash




app=APIRouter()
password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)
@app.post("/register",response_model=UserResponse)
async def register_user(user:UserRegistration):
    existing_user=await collection.find_one({"email":user.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user_dict=user.model_dump()
    user_dict["created_at"]=datetime.utcnow()
    user_dict["is_active"]=True
    user_dict["password"]=get_password_hash(user.password)
    result=await collection.insert_one(user_dict)
    return {
        "message":"User registered successfully",
        "user_id": str(result.inserted_id),
        "name": user.name,
        "email": user.email}

@app.post("/login")
async def login_user(user:login_user):
    db_user=await collection.find_one({"email":user.email})
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email ")
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    token=create_access_token({"user_id": str(db_user["_id"]), "email": db_user["email"]})
    return {"token":token}



@app.get("/profile",response_model=UserResponse)
async def profile(user:dict=Depends(get_current_user)):

    return {
        "user_id": str(user.get("_id")),
        "name": user.get("name"),
        "email": user.get("email")
    }





@app.post("/logout")
async def logout(request: Request, user=Depends(verify_token)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or " " not in auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = auth_header.split(" ")[1]

    # Store the token in Redis blacklist without expiration
    await redis_client.set(token, "blacklisted")

    return {"message": "Logged out successfully"}
