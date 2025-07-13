from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class InquiryRequest(BaseModel):
    inquiry_id: str = Field(..., alias="Inquiry ID")
    listing_id: str = Field(..., alias="Listing ID")
    name: str = Field(..., alias="Inquirer Name")
    email: EmailStr = Field(..., alias="Inquirer Email")
    message: str = Field(..., alias="Message")
    date: str = Field(..., alias="Date")
    phone_number: Optional[str] = Field(None, alias="Phone Number")

    class Config:
        allow_population_by_field_name = True


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


class JobMetadata(BaseModel):
    job_id: str
    progress: int
    total: int
    status: str


class BatchJobResponse(BaseModel):
    job_id: str


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
