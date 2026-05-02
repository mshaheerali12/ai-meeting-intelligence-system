from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth_service.database import collection1,collection0
from fastapi import Depends, HTTPException
from langsmith import traceable
import jwt
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Fix Issue 1 — was hardcoded, now reads from .env correctly
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set in environment variables")


@traceable(name="create access token")
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


security = HTTPBearer()


@traceable(name="verify token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    blacklisted = await collection0.find_one({"token":token})
    if blacklisted:
        raise HTTPException(status_code=401, detail="Token has been revoked")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        user_id = payload.get("user_id")

        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Token signature is invalid")

    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token is malformed")

    except Exception as e:
        logger.error(f"[verify_token ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Token validation failed")


@traceable(name="get current user")
async def get_current_user(payload: dict = Depends(verify_token)):
    email = payload["email"]
    user = await collection1.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
