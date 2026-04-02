"""Document schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.document import DocumentStatus


class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str = Field(..., description="Document filename")
    content_type: Optional[str] = Field(None, description="MIME type of the document")


class DocumentCreate(DocumentBase):
    """Document creation schema."""
    file_hash: str = Field(..., description="SHA256 hash of the file")
    file_size: int = Field(..., description="Size of the file in bytes")
    storage_url: str = Field(..., description="URL where the file is stored")
    user_id: str = Field(..., description="ID of the user who uploaded the document")


class DocumentUpdate(BaseModel):
    """Document update schema."""
    status: Optional[DocumentStatus] = None
    processing_error: Optional[str] = None
    metadata: Optional[dict] = None


class DocumentResponse(DocumentBase):
    """Document response schema."""
    id: str
    file_hash: str
    file_size: int
    status: DocumentStatus
    storage_url: str
    user_id: str
    processing_error: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    documents: list[DocumentResponse]
    total: int
    page: int
    per_page: int