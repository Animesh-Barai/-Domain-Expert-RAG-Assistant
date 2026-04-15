"""Chat schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatBase(BaseModel):
    """Base chat schema."""
    title: str = Field(..., description="Chat title")


class ChatCreate(ChatBase):
    """Chat creation schema."""
    pass


class ChatUpdate(BaseModel):
    """Chat update schema."""
    title: Optional[str] = None


class ChatResponse(ChatBase):
    """Chat response schema."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatWithMessages(ChatResponse):
    """Chat response with messages included."""
    messages: list["MessageResponse"] = []


# Import at the end to avoid circular imports
from app.schemas.message import MessageResponse