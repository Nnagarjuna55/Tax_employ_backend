"""
Content data models and schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Content type enumeration"""
    ARTICLES = "articles"
    NEWS = "news"
    JUDICIARY = "judiciary"
    OTHERS = "others"


class ContentCategory(str, Enum):
    """Content category enumeration"""
    INCOME_TAX = "income-tax"
    GST = "gst"
    MCA = "mca"
    SEBI = "sebi"
    MS_OFFICE = "ms-office"


class ContentBase(BaseModel):
    """Base content model"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Content title"
    )
    type: ContentType = Field(..., description="Content type")
    category: ContentCategory = Field(..., description="Content category")
    body: str = Field(
        ...,
        min_length=10,
        description="Content body"
    )
    summary: Optional[str] = Field(
        None,
        max_length=500,
        description="Content summary"
    )
    author: Optional[str] = Field(
        None,
        max_length=200,
        description="Author name"
    )
    images: Optional[List[str]] = Field(
        None,
        description="List of image URLs"
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('body')
    @classmethod
    def validate_body(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Body must be at least 10 characters')
        return v.strip()


class ContentCreate(ContentBase):
    """Schema for creating content"""
    pass


class ContentUpdate(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Content title"
    )
    type: Optional[ContentType] = Field(None, description="Content type")
    category: Optional[ContentCategory] = Field(None, description="Content category")
    body: Optional[str] = Field(None, min_length=10, description="Content body")
    summary: Optional[str] = Field(None, max_length=500, description="Content summary")
    
    model_config = ConfigDict(from_attributes=True)


class ContentResponse(ContentBase):
    """Schema for content response"""
    id: Optional[str] = Field(None, alias="_id")
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    author: Optional[str] = None
    images: Optional[List[str]] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ContentListResponse(BaseModel):
    """Schema for content list response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ContentResponse]


class BulkSeedResponse(BaseModel):
    """Schema for bulk seed response"""
    count: int
    message: str
    items: List[ContentResponse]
