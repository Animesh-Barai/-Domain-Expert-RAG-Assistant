"""Document processing service."""

from typing import Optional

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.document import Document
from worker.celery_app import celery_app

settings = get_settings()


class DocumentService:
    """Service for document processing operations."""

    async def queue_for_processing(self, document_id: str) -> None:
        """Queue a document for processing."""
        # Send task to Celery
        celery_app.send_task(
            "worker.process_document",
            args=[document_id],
            queue=settings.CELERY_QUEUE_NAME,
        )

    async def get_processing_status(self, document_id: str) -> Optional[str]:
        """Get the processing status of a document."""
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                return document.status
            return None
        finally:
            db.close()

    async def retry_processing(self, document_id: str) -> None:
        """Retry processing a failed document."""
        celery_app.send_task(
            "worker.process_document",
            args=[document_id],
            queue=settings.CELERY_QUEUE_NAME,
        )