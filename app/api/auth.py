"""
Authentication API Routes
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from datetime import datetime
from typing import Optional
import hashlib
import logging

from ..schemas.auth import LoginRequest, LoginResponse, UserCreate, UserResponse
from ..core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Authentication"])

# Simple token storage (in production, use JWT or session management)
SECRET_KEY = "-secret-key-change-in-production"


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    users_collection = db.get_collection("users")
    user = await users_collection.find_one({"token": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return user


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login user and return access token"""
    users_collection = db.get_collection("users")
    
    # Find user
    logger.info(f"Attempting login for email: {login_data.email}")
    user = await users_collection.find_one({"email": login_data.email})
    if not user:
        logger.warning(f"User not found: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    hashed_password = hash_password(login_data.password)
    logger.info(f"Password check: input_hash={hashed_password[:16]}..., stored_hash={user.get('password', '')[:16]}...")
    if user.get("password") != hashed_password:
        logger.warning(f"Password mismatch for {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate simple token (in production, use JWT)
    import secrets
    token = secrets.token_urlsafe(32)
    
    # Store token in user document
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"token": token, "last_login": datetime.utcnow()}}
    )
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", ""),
            "is_admin": user.get("is_admin", False)
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user.get("name", ""),
        is_admin=current_user.get("is_admin", False)
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Logout user"""
    users_collection = db.get_collection("users")
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$unset": {"token": ""}}
    )
    return {"message": "Logged out successfully"}

