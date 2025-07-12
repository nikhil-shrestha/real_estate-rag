from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from app.core.retrieval import get_vectorstore
from app.utils.document_builder import build_documents_from_csv
import logging
from more_itertools import chunked

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/listings")
async def ingest_listings():
    """
    Ingest a CSV file of real estate listings and add them to the vectorstore.
    If no file is uploaded, fallback to local path.
    """
    try:
        # Read DataFrame from upload or fallback
        csv_path = "data/real_estate_listings_750_final.csv"
        df = pd.read_csv(csv_path)

        # Build LangChain documents
        documents = build_documents_from_csv(df)
        logger.info(f"Built {len(documents)} document chunks")

        # Batch insert into vectorstore (Chroma max batch size ~5461)
        batch_size = 5000
        total = 0
        vectorstore = get_vectorstore()

        for batch in chunked(documents, batch_size):
            vectorstore.add_documents(batch)
            total += len(batch)

        logger.info(f"Ingested {total} documents into vectorstore")

        return {
            "status": "success",
            "rows_read": len(df),
            "chunks_ingested": total,
        }

    except Exception as e:
        logger.exception("Failed to ingest listings")
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {e}")