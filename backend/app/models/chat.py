"""Chat model."""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID

from .base import BaseModel


class Chat(BaseModel):
    """Chat model for storing conversation sessions."""
    __tablename__ = "chats"

    user_id = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)

    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self):
        """Return string representation of the chat."""
        return f"<Chat(id={self.id}, title={self.title})>"