"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=200)


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    name: str
    is_admin: bool = False

