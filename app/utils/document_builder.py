# app/utils/document_builder.py

import pandas as pd
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def build_documents_from_csv(df: pd.DataFrame, chunk_size=1000, chunk_overlap=100):
    """
    Convert a DataFrame of listings into LangChain Document chunks using semantic text formatting
    and recursive character splitting.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )

    documents = []

    for _, row in df.iterrows():
        if row.isnull().all():
            continue  # Skip empty rows

        # Build a semantically rich string
        content = (
            f"{str(row.get('Title', '')).strip()}.\n"
            f"Located at {str(row.get('Address', '')).strip()}, "
            f"{str(row.get('City', '')).strip()}, "
            f"{str(row.get('State/Province', '')).strip()} "
            f"{str(row.get('ZIP/Postal Code', '')).strip()}.\n"
            f"Price: ${str(row.get('Price', 'N/A')).strip()}, "
            f"{str(row.get('Bedrooms', 'N/A')).strip()} bedrooms, "
            f"{str(row.get('Bathrooms', 'N/A')).strip()} bathrooms, "
            f"{str(row.get('Square Footage', 'N/A')).strip()} sq ft.\n"
            f"Amenities: {str(row.get('Amenities', 'N/A')).strip()}."
        ).replace("  ", " ").replace(" .", ".").strip()

        # Split into chunks
        chunks = text_splitter.split_text(content)

        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "listing_id": row.get("Listing ID", None),
                        "city": str(row.get("City", "")).strip(),
                        "price": row.get("Price", None),
                        "bedrooms": row.get("Bedrooms", None),
                        "bathrooms": row.get("Bathrooms", None),
                    }
                )
            )

    return documents
