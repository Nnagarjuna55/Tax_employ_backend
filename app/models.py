"""
Pydantic models for  API
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ContentModel(BaseModel):
    """Content model for API responses"""
    id: Optional[str] = Field(default=None, alias="_id")
    title: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., description="Type: articles, news, judiciary, or others")
    category: str = Field(..., description="Category: income-tax, gst, mca, sebi, or ms-office")
    body: str = Field(..., min_length=10)
    summary: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "title": "New Tax Slabs 2025",
                "type": "news",
                "category": "income-tax",
                "body": "Detailed explanation of new tax slabs and their implications for taxpayers...",
                "summary": "Overview of new tax slabs",
                "date": "2024-01-15T00:00:00"
            }
        }

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        allowed_types = ['articles', 'news', 'judiciary', 'others']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of {allowed_types}')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        allowed_categories = ['income-tax', 'gst', 'mca', 'sebi', 'ms-office']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of {allowed_categories}')
        return v


class CreateContentSchema(BaseModel):
    """Schema for creating content"""
    title: str = Field(..., min_length=1, max_length=500)
    type: str
    category: str
    body: str = Field(..., min_length=10)
    summary: Optional[str] = Field(None, max_length=500)

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        allowed_types = ['articles', 'news', 'judiciary', 'others']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of {allowed_types}')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        allowed_categories = ['income-tax', 'gst', 'mca', 'sebi', 'ms-office']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of {allowed_categories}')
        return v


class UpdateContentSchema(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    body: Optional[str] = Field(None, min_length=10)
    summary: Optional[str] = Field(None, max_length=500)


class ContactModel(BaseModel):
    """Contact form model"""
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=5000)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "message": "I have a question about tax compliance..."
            }
        }


class ContactResponseModel(BaseModel):
    """Contact response model"""
    id: str
    name: str
    email: str
    message: str
    date: datetime
    status: Optional[str] = "new"

