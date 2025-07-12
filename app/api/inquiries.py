from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Query
import io
import pandas as pd
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.schemas import (
    InquiryRequest, 
    InquiryResponse, 
    InquiryHistoryResponse,
    BatchInquiryRequest,
    InquiryAnalyticsResponse,
    InquiryStatusResponse
)
from app.services.processor import process_inquiry
from app.services.batch_processor import process_batch_inquiries
# from app.services.analytics_service import get_inquiry_analytics
from app.db.session import get_db
from app.db.models import InquiryHistory
from app.core.retrieval import get_retriever
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


# Core inquiry processing endpoints
@router.post("/process", response_model=InquiryResponse)
async def process_single_inquiry(
    request: InquiryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process a single real estate inquiry with AI-powered response generation
    """
    try:
        logger.info(f"Processing inquiry from {request.email}")
        
        # Generate unique processing ID for tracking
        processing_id = str(uuid.uuid4())
        
        # Process the inquiry
        result = process_inquiry(request)
        
        # Add processing metadata
        result['processing_id'] = processing_id
        result['processed_at'] = datetime.utcnow().isoformat()
        
        # Save to database in background
        background_tasks.add_task(
            save_inquiry_to_db,
            request=request,
            result=result,
            db_session=db
        )
        
        logger.info(f"Inquiry processed successfully with ID: {processing_id}")
        return InquiryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing inquiry: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process inquiry: {str(e)}"
        )


@router.post("/process/batch", response_model=List[InquiryResponse])
async def process_batch_inquiries_endpoint(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Process multiple inquiries via file upload (CSV or JSON)
    """
    try:
        filename = file.filename.lower()

        if filename.endswith(".csv"):
            contents = await file.read()
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

            # Transform CSV rows into InquiryRequest schema
            inquiries = []
            for _, row in df.iterrows():
                try:
                    inquiry = InquiryRequest(
                        listing_id=str(row["Listing ID"]),
                        name=str(row["Inquirer Name"]),
                        email=str(row["Inquirer Email"]),
                        message=str(row["Message"]),
                        phone_number=str(row.get("Phone Number", ""))
                    )
                    inquiries.append(inquiry)
                except Exception as parse_err:
                    logger.warning(f"Skipping malformed row: {row} — {parse_err}")

        elif filename.endswith(".json"):
            contents = await file.read()
            raw = json.loads(contents)
            inquiries = [InquiryRequest(**item) for item in raw]

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use .csv or .json")

        if not inquiries:
            raise HTTPException(status_code=400, detail="No valid inquiries found in file")

        logger.info(f"Processing batch of {len(inquiries)} inquiries from {filename}")

        # Process all inquiries
        results = process_batch_inquiries(inquiries)

        # Save to DB in background
        background_tasks.add_task(
            save_batch_inquiries_to_db,
            inquiries=inquiries,
            results=results,
            db_session=db
        )

        return results

    except Exception as e:
        logger.exception("Failed to process batch inquiries")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# Inquiry history and tracking endpoints
@router.get("/history", response_model=List[InquiryHistoryResponse])
async def get_inquiry_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    email: Optional[str] = Query(None, description="Filter by email address"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    Get inquiry history with advanced filtering options
    """
    try:
        # Build query with filters
        query = db.query(InquiryHistory)
        
        if email:
            query = query.filter(InquiryHistory.email == email)
        
        if category:
            query = query.filter(InquiryHistory.category == category)
        
        if date_from:
            query = query.filter(InquiryHistory.created_at >= date_from)
        
        if date_to:
            query = query.filter(InquiryHistory.created_at <= date_to)
        
        # Apply pagination and ordering
        rows = query.order_by(desc(InquiryHistory.created_at)).offset(skip).limit(limit).all()
        
        return [
            InquiryHistoryResponse(
                id=row.id,
                email=row.email,
                category=row.category,
                message=row.message,
                response=row.response,
                # email_title=row.email_title,
                # email_body=row.email_body,
                listing_id=row.listing_id,
                created_at=row.created_at
            ) for row in rows
        ]
        
    except Exception as e:
        logger.error(f"Error fetching inquiry history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history/{inquiry_id}", response_model=InquiryHistoryResponse)
async def get_inquiry_by_id(
    inquiry_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific inquiry by ID
    """
    try:
        row = db.query(InquiryHistory).filter(InquiryHistory.id == inquiry_id).first()
        
        if not row:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        
        return InquiryHistoryResponse(
            id=row.id,
            email=row.email,
            category=row.category,
            message=row.message,
            response=row.response,
            # email_title=row.email_title,
            # email_body=row.email_body,
            listing_id=row.listing_id,
            created_at=row.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inquiry {inquiry_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Analytics and insights endpoints
@router.get("/analytics", response_model=InquiryAnalyticsResponse)
async def get_inquiry_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get analytics and insights about inquiry patterns
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get basic statistics
        total_inquiries = db.query(InquiryHistory).filter(
            InquiryHistory.created_at >= start_date
        ).count()
        
        # Category distribution
        category_stats = db.query(
            InquiryHistory.category,
            func.count(InquiryHistory.id).label('count')
        ).filter(
            InquiryHistory.created_at >= start_date
        ).group_by(InquiryHistory.category).all()
        
        # Daily inquiry counts
        daily_stats = db.query(
            func.date(InquiryHistory.created_at).label('date'),
            func.count(InquiryHistory.id).label('count')
        ).filter(
            InquiryHistory.created_at >= start_date
        ).group_by(func.date(InquiryHistory.created_at)).all()
        
        # Top inquiring emails
        top_users = db.query(
            InquiryHistory.email,
            func.count(InquiryHistory.id).label('count')
        ).filter(
            InquiryHistory.created_at >= start_date
        ).group_by(InquiryHistory.email).order_by(
            desc(func.count(InquiryHistory.id))
        ).limit(10).all()
        
        return InquiryAnalyticsResponse(
            total_inquiries=total_inquiries,
            date_range_days=days,
            category_distribution={cat: count for cat, count in category_stats},
            daily_counts={str(date): count for date, count in daily_stats},
            top_users=[{"email": email, "count": count} for email, count in top_users]
        )
        
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Status and health check endpoints
@router.get("/status", response_model=InquiryStatusResponse)
async def get_processing_status(db: Session = Depends(get_db)):
    """
    Get current system status and processing capabilities
    """
    try:
        # Check database connectivity
        db_status = "healthy"
        try:
            db.execute("SELECT 1")
        except:
            db_status = "unhealthy"
        
        # Check vector store connectivity
        vectorstore_status = "healthy"
        try:
            retriever = get_retriever()
            # Try a simple retrieval test
            retriever.get_relevant_documents("test")
        except:
            vectorstore_status = "unhealthy"
        
        # Get recent processing stats
        recent_inquiries = db.query(InquiryHistory).filter(
            InquiryHistory.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        return InquiryStatusResponse(
            status="healthy" if db_status == "healthy" and vectorstore_status == "healthy" else "degraded",
            database_status=db_status,
            vectorstore_status=vectorstore_status,
            recent_inquiries_count=recent_inquiries,
            last_check=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error checking system status: {e}")
        return InquiryStatusResponse(
            status="unhealthy",
            database_status="unknown",
            vectorstore_status="unknown",
            recent_inquiries_count=0,
            last_check=datetime.utcnow().isoformat(),
            error_message=str(e)
        )


# Search and filtering endpoints
@router.get("/search", response_model=List[InquiryHistoryResponse])
async def search_inquiries(
    query: str = Query(..., description="Search query"),
    search_in: str = Query("message", description="Field to search in: message, response, email"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Search through inquiry history using text search
    """
    try:
        # Build search query based on field
        if search_in == "message":
            results = db.query(InquiryHistory).filter(
                InquiryHistory.message.contains(query)
            ).limit(limit).all()
        elif search_in == "response":
            results = db.query(InquiryHistory).filter(
                InquiryHistory.response.contains(query)
            ).limit(limit).all()
        elif search_in == "email":
            results = db.query(InquiryHistory).filter(
                InquiryHistory.email.contains(query)
            ).limit(limit).all()
        else:
            # Search in all fields
            results = db.query(InquiryHistory).filter(
                InquiryHistory.message.contains(query) |
                InquiryHistory.response.contains(query) |
                InquiryHistory.email.contains(query)
            ).limit(limit).all()
        
        return [
            InquiryHistoryResponse(
                id=row.id,
                email=row.email,
                category=row.category,
                message=row.message,
                response=row.response,
                email_title=row.email_title,
                email_body=row.email_body,
                listing_id=row.listing_id,
                created_at=row.created_at
            ) for row in results
        ]
        
    except Exception as e:
        logger.error(f"Error searching inquiries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Helper functions for background tasks
async def save_inquiry_to_db(request: InquiryRequest, result: Dict[str, Any], db_session: Session):
    """Save single inquiry to database"""
    try:
        record = InquiryHistory(
            email=request.email,
            category=result['category'],
            message=request.message,
            response=result['response'],
            email_title=result.get('email_title'),
            email_body=result.get('email_body'),
            listing_id=request.listing_id
        )
        db_session.add(record)
        db_session.commit()
        logger.info(f"Inquiry saved to database for {request.email}")
    except Exception as e:
        logger.error(f"Failed to save inquiry to database: {e}")
        db_session.rollback()


async def save_batch_inquiries_to_db(inquiries: List[InquiryRequest], results: List[Dict[str, Any]], db_session: Session):
    """Save batch inquiries to database"""
    try:
        records = []
        for inquiry, result in zip(inquiries, results):
            record = InquiryHistory(
                email=inquiry.email,
                category=result['category'],
                message=inquiry.message,
                response=result['response'],
                email_title=result.get('email_title'),
                email_body=result.get('email_body'),
                listing_id=inquiry.listing_id
            )
            records.append(record)
        
        db_session.bulk_save_objects(records)
        db_session.commit()
        logger.info(f"Batch of {len(records)} inquiries saved to database")
    except Exception as e:
        logger.error(f"Failed to save batch inquiries to database: {e}")
        db_session.rollback()