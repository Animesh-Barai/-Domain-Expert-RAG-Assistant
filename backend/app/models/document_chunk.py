"""Document chunk model for storing text fragments."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DocumentChunk(BaseModel):
    """Model for storing document text chunks."""

    __tablename__ = "document_chunks"

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)  # Optional page number
    chunk_metadata = Column(String(1024), nullable=True)  # JSON metadata

    # Relationships
    document = relationship("Document", back_populates="chunks")