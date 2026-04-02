"""Message schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.message import MessageRole


class MessageBase(BaseModel):
    """Base message schema."""
    content: str = Field(..., description="Message content")


class MessageCreate(MessageBase):
    """Message creation schema."""
    pass


class MessageUpdate(BaseModel):
    """Message update schema."""
    content: Optional[str] = None


class MessageResponse(MessageBase):
    """Message response schema."""
    id: str
    chat_id: str
    role: MessageRole
    created_at: datetime

    class Config:
        from_attributes = True


class MessageWithChat(MessageResponse):
    """Message response with chat included."""
    chat: "ChatResponse" = {}


# Import at the end to avoid circular imports
from app.schemas.chat import ChatResponse