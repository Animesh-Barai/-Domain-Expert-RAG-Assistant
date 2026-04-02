"""Message model."""

import enum
from sqlalchemy import Column, Enum, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class MessageRole(str, enum.Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Message model for storing chat messages."""
    __tablename__ = "messages"

    chat_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    # Store document IDs used as citations for this message
    citations = Column(JSON, nullable=True)

    # Relationships
    chat = relationship("Chat", back_populates="messages")
    # Many-to-many relationship with documents
    documents = relationship(
        "Document",
        secondary="message_documents",
        back_populates="messages",
    )

    def __repr__(self):
        """Return string representation of the message."""
        return f"<Message(id={self.id}, role={self.role}, chat_id={self.chat_id})>"


# Association table for many-to-many relationship between messages and documents
from sqlalchemy import Table, MetaData

metadata = MetaData()

message_documents = Table(
    "message_documents",
    BaseModel.metadata,
    Column(
        "message_id",
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "document_id",
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)