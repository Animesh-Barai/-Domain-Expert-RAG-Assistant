"""Processing task model for tracking background jobs."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ProcessingTask(BaseModel):
    """Model for tracking background processing tasks."""

    __tablename__ = "processing_tasks"

    task_id = Column(String(255), nullable=False, unique=True, index=True)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_type = Column(String(50), nullable=False)  # e.g., "process_document"
    status = Column(String(20), nullable=False, default="PENDING")
    progress = Column(String(10), nullable=True)  # "0-100"
    result = Column(JSONB, nullable=True)  # Task result data
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(String(10), nullable=False, default="0")
    max_retries = Column(String(10), nullable=False, default="3")
    task_metadata = Column(JSONB, nullable=True)  # Additional task metadata

    # Relationships
    document = relationship("Document", back_populates="processing_tasks")

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status in ["COMPLETED", "FAILED"]

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate task duration in seconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None