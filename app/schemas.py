from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class InquiryRequest(BaseModel):
    listing_id: str
    name: str
    email: str
    message: str
    phone_number: Optional[str] = None


class InquiryResponse(BaseModel):
    email: EmailStr
    category: str
    response: str
    email_title: Optional[str] = None
    email_body: Optional[str] = None
    processing_id: Optional[str] = None
    processed_at: Optional[str] = None


class InquiryHistoryResponse(BaseModel):
    id: int
    email: EmailStr
    category: str
    message: str
    response: str
    email_title: Optional[str] = None
    email_body: Optional[str] = None
    listing_id: Optional[str] = None
    created_at: datetime


class BatchInquiryRequest(BaseModel):
    inquiries: List[InquiryRequest]
    
    @validator('inquiries')
    def validate_inquiries(cls, v):
        if len(v) > 100:
            raise ValueError('Batch size cannot exceed 100 inquiries')
        if len(v) == 0:
            raise ValueError('Batch must contain at least one inquiry')
        return v


class InquiryAnalyticsResponse(BaseModel):
    total_inquiries: int
    date_range_days: int
    category_distribution: Dict[str, int]
    daily_counts: Dict[str, int]
    top_users: List[Dict[str, Any]]


class InquiryStatusResponse(BaseModel):
    status: str
    database_status: str
    vectorstore_status: str
    recent_inquiries_count: int
    last_check: str
    error_message: Optional[str] = None