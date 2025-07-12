from app.core.retrieval import get_retriever
from app.core.llm import llm, category_chain, expand_chain, category_prompts, parser
from app.services.email import send_email_via_agent
from app.config import config
from langchain.schema.runnable import RunnableMap, RunnablePassthrough
from app.schemas import InquiryRequest
import logging

logger = logging.getLogger(__name__)


def process_inquiry(request: InquiryRequest) -> dict:
    """Process a real estate inquiry end-to-end"""

    try:
        raw_query = request.message
        logger.info(f"Processing inquiry from {request.email}")

        # Step 1: Expand the inquiry message
        try:
            expanded = expand_chain.invoke({"message": raw_query})
            logger.debug(f"Expanded query: {expanded}")
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}, using raw query")
            expanded = raw_query

        # Step 2: Categorize the inquiry
        try:
            category = category_chain.invoke({"message": raw_query}).strip()
            logger.info(f"Inquiry categorized as: {category}")
        except Exception as e:
            logger.error(f"Inquiry categorization failed: {e}")
            category = "General Inquiry"

        # Step 3: Generate a response using RAG
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
            logger.info("Successfully generated response via RAG")

        except Exception as e:
            logger.error(f"RAG response generation failed: {e}")
            response = (
                "We're currently unable to process your request. "
                "Please contact support or try again later."
            )

        # Step 4: Email the response if enabled
        if config.EMAIL_ENABLED:
            try:
                subject = f"Re: Your Real Estate Inquiry - {category}"
                send_email_via_agent(
                    to=request.email,
                    subject=subject,
                    body=response
                )
                logger.info(f"Email successfully sent to {request.email}")
            except Exception as e:
                logger.error(f"Email sending failed for {request.email}: {e}")

        return {
            "email": request.email,
            "category": category,
            "response": response
        }

    except Exception as e:
        logger.exception("Unhandled exception while processing inquiry")
        return {
            "email": request.email,
            "category": "Unknown",
            "response": (
                "An unexpected error occurred while processing your inquiry. "
                "Please try again later or contact support."
            )
        }