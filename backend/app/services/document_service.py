"""Document processing service."""

from typing import Optional

from app.core.config import get_settings
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
        # This would typically check the database or a cache
        # For now, we'll implement this as a stub
        pass

    async def retry_processing(self, document_id: str) -> None:
        """Retry processing a failed document."""
        celery_app.send_task(
            "worker.process_document",
            args=[document_id],
            queue=settings.CELERY_QUEUE_NAME,
        )