from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from auth_service.database import collection1,collection0
from auth_service.schemas import UserRegistration, login_user, UserResponse
from auth_service.security import create_access_token, verify_token, get_current_user
from datetime import datetime,timedelta

from pwdlib import PasswordHash
from langsmith import traceable
from bson import ObjectId
import logging
import os

logger = logging.getLogger(__name__)
app = APIRouter()
password_hash = PasswordHash.recommended()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


@app.post("/register", response_model=UserResponse)
async def register_user(user: UserRegistration):
    try:
        existing_user = await collection1.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user_dict = user.model_dump()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["is_active"] = True
        user_dict["password"] = get_password_hash(user.password)

        result = await collection1.insert_one(user_dict)
        logger.info(f"New user registered: email={user.email}")

        # Explicitly construct UserResponse — avoids ObjectId serialization error
        return UserResponse(
            user_id=str(result.inserted_id),
            name=user.name,
            email=user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Register ERROR] email={user.email} error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


@app.post("/login")
async def login(user: login_user):
    try:
        db_user = await collection1.find_one({"email": user.email})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(user.password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not db_user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        token = create_access_token({
            "user_id": str(db_user["_id"]),
            "email": db_user["email"]
        })

        logger.info(f"User logged in: email={user.email}")
        return {
            "token": token,
            "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Login ERROR] email={user.email} error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")


@app.get("/profile", response_model=UserResponse)
async def profile(user: dict = Depends(get_current_user)):
    try:
        # Explicitly construct UserResponse — avoids ObjectId serialization error
        return UserResponse(
            user_id=str(user.get("_id")),
            name=user.get("name", ""),
            email=user.get("email", "")
        )
    except Exception as e:
        logger.error(f"[Profile ERROR] error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not fetch profile.")


@app.post("/logout")
async def logout(request: Request, user=Depends(verify_token)):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or " " not in auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = auth_header.split(" ")[1]

        # Blacklist with TTL — prevents unbounded Redis memory growth
        await collection0.insert_one({
            "token": token,
            "user_id": user.get("user_id"),
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow()+timedelta(ACCESS_TOKEN_EXPIRE_MINUTES) 
        })

        logger.info(f"User logged out: email={user.get('email')}")
        return {"message": "Logged out successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Logout ERROR] error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Logout failed. Please try again.")
