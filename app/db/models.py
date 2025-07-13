from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.session import Base
from datetime import datetime


class InquiryHistory(Base):
    __tablename__ = "inquiry_history"

    id = Column(Integer, primary_key=True, index=True)  # Local DB ID
    inquiry_id = Column(String, nullable=True)          # Inquiry ID from the file
    listing_id = Column(String, nullable=True)          # Listing ID
    name = Column(String, nullable=True)                # Inquirer Name
    email = Column(String, nullable=False)              # Inquirer Email
    phone_number = Column(String, nullable=True)        # Phone Number
    message = Column(Text, nullable=True)               # Inquiry message
    category = Column(String, nullable=True)            # AI-determined category
    response = Column(Text, nullable=True)              # AI-generated response
    email_title = Column(String, nullable=True)         # Email subject (optional)
    email_body = Column(Text, nullable=True)            # Email body (optional)
    file_date = Column(String, nullable=True)           # Date from file (string parsed)
    created_at = Column(DateTime, default=datetime.utcnow)  # Record creation timestamp