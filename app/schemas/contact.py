"""
Contact data models and schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContactStatus(str, Enum):
    """Contact submission status"""
    NEW = "new"
    REVIEWED = "reviewed"
    REPLIED = "replied"
    ARCHIVED = "archived"


class ContactBase(BaseModel):
    """Base contact model"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Contact name"
    )
    email: EmailStr = Field(..., description="Contact email")
    message: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Contact message"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters')
        return v.strip()


class ContactCreate(ContactBase):
    """Schema for creating contact"""
    pass


class ContactResponse(ContactBase):
    """Schema for contact response"""
    id: Optional[str] = Field(None, alias="_id")
    status: ContactStatus = Field(default=ContactStatus.NEW)
    date: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ContactListResponse(BaseModel):
    """Schema for contact list response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ContactResponse]


class ContactCountResponse(BaseModel):
    """Schema for contact count response"""
    count: int
    new_count: int
    reviewed_count: int
    replied_count: int
    archived_count: int
