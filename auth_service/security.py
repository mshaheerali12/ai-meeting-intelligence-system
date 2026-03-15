from datetime import datetime,timedelta
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from auth_service.database import collection
from fastapi import Depends,HTTPException
from transcription.redis_db import redis_client
import jwt
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token
security=HTTPBearer()
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
   

    token = credentials.credentials
    blacklisted = await redis_client.get(token)
    if blacklisted:
        raise HTTPException(status_code=401, detail="Token has been revoked")

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        email = payload.get("email")
        user_id = payload.get("user_id")

        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token:{e}")
async def get_current_user(payload: dict = Depends(verify_token)):
    
    email = payload["email"]

    user = await collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user