"""User model."""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """User model for authentication and user management."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_active(self):
        return True


    def __repr__(self):
        """Return string representation of the user."""
        return f"<User(id={self.id}, email={self.email})>"