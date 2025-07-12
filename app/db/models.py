from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.session import Base
from datetime import datetime


class InquiryHistory(Base):
    __tablename__ = "inquiry_history"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    category = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    listing_id = Column(String, nullable=True)
    # email_title = Column(String, nullable=True)
    # email_body = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)