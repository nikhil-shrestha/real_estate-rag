import os
from dotenv import load_dotenv
from typing import Optional
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    # Database
    DB_URL: str = os.getenv("DATABASE_URL", "sqlite:///./real_estate.db")
    
    # Vector Store
    CHROMA_DIR: str = os.getenv("CHROMA_DB", "chroma_db")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Email
    GMAIL_SENDER: Optional[str] = os.getenv("GMAIL_SENDER")
    GMAIL_PASSWORD: Optional[str] = os.getenv("GMAIL_PASSWORD")
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
    
    # Application
    MAX_RETRIEVAL_DOCS: int = int(os.getenv("MAX_RETRIEVAL_DOCS", "5"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    
    def validate(self):
        """Validate required configuration"""
        missing = []
        
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        
        if self.EMAIL_ENABLED and not self.GMAIL_SENDER:
            missing.append("GMAIL_SENDER")
        
        if self.EMAIL_ENABLED and not self.GMAIL_PASSWORD:
            missing.append("GMAIL_PASSWORD")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        logger.info("Configuration validated successfully")


config = Config()
config.validate()