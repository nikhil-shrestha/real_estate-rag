from app.core.llm import expand_chain, category_chain, category_prompts, llm, parser
from app.core.retrieval import get_retriever
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from app.schemas import InquiryRequest
from app.config import config
from app.services.email import send_email
import logging

logger = logging.getLogger(__name__)


def process_inquiry(request: InquiryRequest) -> dict:
    """Process a real estate inquiry with enhanced error handling"""
    
    try:
        # Step 1: Expand the query for better retrieval
        raw_query = request.message
        logger.info(f"Processing inquiry from {request.email}")
        
        try:
            expanded = expand_chain.invoke({"message": raw_query})
            logger.debug(f"Query expanded: {expanded}")
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}. Using original query.")
            expanded = raw_query

        # Step 2: Categorize the inquiry
        try:
            category = category_chain.invoke({"message": raw_query}).strip()
            logger.info(f"Inquiry categorized as: {category}")
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            category = "General Inquiry"

        # Step 3: Generate response using RAG
        try:
            retriever = get_retriever()
            
            response_chain = (
                RunnableMap({
                    "context": retriever, 
                    "question": RunnablePassthrough()
                }) |
                category_prompts.get(category, category_prompts["General Inquiry"]) |
                llm |
                parser
            )
            
            response = response_chain.invoke(expanded)
            logger.info(f"Response generated successfully")
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            response = "I apologize, but I'm having trouble processing your inquiry right now. Please try again later or contact our support team directly."

        # Step 4: Send email notification
        if config.EMAIL_ENABLED:
            try:
                send_email(
                    to_address=request.email,
                    subject=f"Re: Your Real Estate Inquiry - {category}",
                    body=response
                )
                logger.info(f"Email sent to {request.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {request.email}: {e}")

        return {
            "email": request.email,
            "category": category,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Unexpected error processing inquiry: {e}")
        return {
            "email": request.email,
            "category": "General Inquiry",
            "response": "I apologize, but I encountered an error processing your inquiry. Please try again later."
        }