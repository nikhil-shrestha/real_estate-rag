from typing import List, Dict, Any
from app.schemas import InquiryRequest
from app.services.processor import process_inquiry
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


def process_batch_inquiries(inquiries: List[InquiryRequest]) -> List[Dict[str, Any]]:
    """
    Process multiple inquiries efficiently using threading
    """
    logger.info(f"Starting batch processing of {len(inquiries)} inquiries")
    start_time = time.time()
    
    results = []
    
    # For small batches, process sequentially
    if len(inquiries) <= 5:
        for inquiry in inquiries:
            try:
                result = process_inquiry(inquiry)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing inquiry from {inquiry.email}: {e}")
                results.append({
                    "email": inquiry.email,
                    "category": "General Inquiry",
                    "response": "Sorry, we encountered an error processing your inquiry.",
                    "email_title": "Error Processing Inquiry",
                    "email_body": "We apologize for the inconvenience. Please try again later."
                })
    else:
        # For larger batches, use thread pool
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_inquiry, inquiry) for inquiry in inquiries]
            
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=30)  # 30 second timeout per inquiry
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing inquiry from {inquiries[i].email}: {e}")
                    results.append({
                        "email": inquiries[i].email,
                        "category": "General Inquiry",
                        "response": "Sorry, we encountered an error processing your inquiry.",
                        "email_title": "Error Processing Inquiry",
                        "email_body": "We apologize for the inconvenience. Please try again later."
                    })
    
    processing_time = time.time() - start_time
    logger.info(f"Batch processing completed in {processing_time:.2f} seconds")
    
    return results