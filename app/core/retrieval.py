from langchain_chroma import Chroma
from app.core.embeddings import get_embedding_model
from app.config import config
import os
import logging

logger = logging.getLogger(__name__)

embedding_model = get_embedding_model()
vectorstore = None
retriever = None


def initialize_vectorstore():
    """Initialize vector store and retriever"""
    global vectorstore, retriever
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(config.CHROMA_DIR, exist_ok=True)
        
        vectorstore = Chroma(
            persist_directory=config.CHROMA_DIR, 
            embedding_function=embedding_model
        )
        
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": config.MAX_RETRIEVAL_DOCS}
        )
        
        logger.info(f"Vector store initialized with {len(vectorstore.get()['documents'])} documents")
        
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        raise


def get_retriever():
    """Get retriever instance"""
    if retriever is None:
        raise RuntimeError("Vector store not initialized. Call initialize_vectorstore() first.")
    return retriever


def get_vectorstore():
    """Get vector store instance"""
    if vectorstore is None:
        raise RuntimeError("Vector store not initialized. Call initialize_vectorstore() first.")
    return vectorstore