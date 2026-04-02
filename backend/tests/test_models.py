"""Test models directly without database."""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.chat import Chat
from app.models.message import Message
from app.models.document_chunk import DocumentChunk
from app.models.processing_task import ProcessingTask
from app.schemas.auth import UserCreate, UserUpdate
from pydantic import ValidationError


class TestUserModel:
    """Test User model."""

    def test_user_creation(self):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.id is None  # Not saved yet

    def test_user_repr(self):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            password_hash="hash",
            full_name="Test User"
        )
        expected = "<User(email=test@example.com, full_name=Test User)>"
        assert repr(user) == expected


class TestDocumentModel:
    """Test Document model."""

    def test_document_creation(self):
        """Test creating a document."""
        doc = Document(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            filename="test.pdf",
            file_hash="abc123",
            storage_url="s3://bucket/test.pdf",
            file_size=1024,
            status=DocumentStatus.PENDING,
            content_type="application/pdf"
        )
        assert doc.filename == "test.pdf"
        assert doc.status == DocumentStatus.PENDING
        assert doc.file_size == 1024

    def test_document_status_enum(self):
        """Test document status enum."""
        assert DocumentStatus.PENDING.value == "PENDING"
        assert DocumentStatus.PROCESSING.value == "PROCESSING"
        assert DocumentStatus.COMPLETED.value == "COMPLETED"
        assert DocumentStatus.FAILED.value == "FAILED"


class TestChatModel:
    """Test Chat model."""

    def test_chat_creation(self):
        """Test creating a chat."""
        chat = Chat(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Chat"
        )
        assert chat.title == "Test Chat"
        assert chat.user_id == "123e4567-e89b-12d3-a456-426614174000"


class TestMessageModel:
    """Test Message model."""

    def test_message_creation(self):
        """Test creating a message."""
        message = Message(
            chat_id="123e4567-e89b-12d3-a456-426614174000",
            role="user",
            content="Hello, world!"
        )
        assert message.role == "user"
        assert message.content == "Hello, world!"


class TestDocumentChunkModel:
    """Test DocumentChunk model."""

    def test_document_chunk_creation(self):
        """Test creating a document chunk."""
        chunk = DocumentChunk(
            document_id="123e4567-e89b-12d3-a456-426614174000",
            content="This is a test chunk",
            chunk_index=0,
            word_count=5,
            page_number=1
        )
        assert chunk.content == "This is a test chunk"
        assert chunk.chunk_index == 0
        assert chunk.word_count == 5
        assert chunk.page_number == 1


class TestProcessingTaskModel:
    """Test ProcessingTask model."""

    def test_processing_task_creation(self):
        """Test creating a processing task."""
        task = ProcessingTask(
            task_id="task-123",
            document_id="123e4567-e89b-12d3-a456-426614174000",
            task_type="process_document",
            status="PENDING",
            retry_count="0",
            max_retries="3"
        )
        assert task.task_id == "task-123"
        assert task.task_type == "process_document"
        assert task.status == "PENDING"

    def test_task_duration(self):
        """Test task duration calculation."""
        from datetime import datetime, timedelta

        task = ProcessingTask(
            task_id="task-123",
            document_id="123e4567-e89b-12d3-a456-426614174000",
            task_type="process_document",
            status="COMPLETED"
        )

        # Test without timestamps
        assert task.duration_seconds is None

        # Test with timestamps
        now = datetime.now()
        later = now + timedelta(seconds=30)
        task.started_at = now
        task.completed_at = later

        assert task.duration_seconds == 30.0


class TestUserSchemas:
    """Test user schemas."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user_data = {
            "email": "test@example.com",
            "password": "strongpassword",
            "full_name": "Test User"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.password == "strongpassword"
        assert user.full_name == "Test User"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        user_data = {
            "email": "not-an-email",
            "password": "password123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_update_partial(self):
        """Test UserUpdate with partial data."""
        update_data = {
            "full_name": "Updated Name"
        }
        user = UserUpdate(**update_data)
        assert user.full_name == "Updated Name"
        assert user.email is None
        assert user.password is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])