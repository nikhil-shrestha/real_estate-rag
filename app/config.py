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
    
    # Email / SMTP
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Real Estate Assistant")
    EMAIL_FROM_ADDRESS: Optional[str] = os.getenv("EMAIL_FROM_ADDRESS", SMTP_USERNAME)

    # Application
    MAX_RETRIEVAL_DOCS: int = int(os.getenv("MAX_RETRIEVAL_DOCS", "5"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    
    def validate(self):
        """Validate required configuration"""
        missing = []
        
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        
        if self.EMAIL_ENABLED:
            if not self.SMTP_USERNAME:
                missing.append("SMTP_USERNAME")
            if not self.SMTP_PASSWORD:
                missing.append("SMTP_PASSWORD")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        logger.info("Configuration validated successfully")


config = Config()
config.validate()