from langchain_openai import OpenAIEmbeddings
from app.config import config
import logging

logger = logging.getLogger(__name__)


def get_embedding_model():
    """Get embedding model with enhanced configuration and error handling"""
    try:
        embedding_model = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY,
            # Add additional parameters for better performance
            chunk_size=1000,  # Number of documents to send in each request
            max_retries=3,    # Number of retries for failed requests
            request_timeout=30.0  # Timeout for requests
        )
        
        logger.info(f"Embedding model initialized: {config.EMBEDDING_MODEL}")
        return embedding_model
        
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        raise RuntimeError(f"Could not initialize embedding model: {e}")