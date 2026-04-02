"""Document model."""

import enum
from sqlalchemy import Column, Enum, ForeignKey, String, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID

from .base import BaseModel


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Document(BaseModel):
    """Document model for storing uploaded file metadata."""
    __tablename__ = "documents"

    user_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True, index=True)
    storage_url = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    content_type = Column(String(100), nullable=False)
    # Store error message if processing failed
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="documents")
    # This will be populated when messages reference this document
    messages = relationship("Message", back_populates="documents", secondary="message_documents")
    # Document chunks created after processing
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    # Processing tasks for this document
    processing_tasks = relationship("ProcessingTask", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        """Return string representation of the document."""
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"