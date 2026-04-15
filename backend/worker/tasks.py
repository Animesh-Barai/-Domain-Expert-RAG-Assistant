"""Celery tasks for document processing."""

import asyncio
import os
import tempfile
from typing import Any

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.ingest.parsing import PDFParser
from app.services.rag_service import RAGService
from app.services.storage_service import StorageService
from worker.celery_app import celery_app

settings = get_settings()


async def _process_document_internal(document_id: str):
    """Internal async processing logic."""
    db = SessionLocal()
    try:
        # 1. Fetch document from DB
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            print(f"Document {document_id} not found in database")
            return

        # 2. Update status to PROCESSING
        document.status = DocumentStatus.PROCESSING
        db.commit()

        # 3. Download from Storage
        storage_service = StorageService()
        file_bytes = await storage_service.download_file(document.storage_url)

        # 4. Save to temporary file for Unstructured/LlamaIndex
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            # 5. Parse Document (Using Semantic Chunking)
            parser = PDFParser()
            nodes = parser.parse_pdf(
                tmp_path, 
                metadata={
                    "document_id": str(document.id),
                    "user_id": str(document.user_id),
                    "filename": document.filename
                }
            )

            # 6. Index into Vector Store
            rag_service = RAGService()
            await rag_service.add_document_to_index(nodes)

            # 7. Update status to COMPLETED
            document.status = DocumentStatus.COMPLETED
            db.commit()

        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")
        # Update status to FAILED
        if 'document' in locals() and document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()
    finally:
        db.close()


@celery_app.task(name="worker.process_document")
def process_document(document_id: str) -> None:
    """Entry point for Celery task (sync wrapper for async logic)."""
    # Use asyncio.run to execute the async internal logic
    asyncio.run(_process_document_internal(document_id))
