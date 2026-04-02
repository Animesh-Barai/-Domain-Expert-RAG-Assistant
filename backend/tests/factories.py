"""Factory classes for creating test data."""

import uuid
from datetime import datetime
from typing import Any, Dict

import faker

# Initialize faker
fake = faker.Faker()


class BaseFactory:
    """Base factory class."""

    @classmethod
    def create(cls, **kwargs: Any) -> Dict[str, Any]:
        """Create a dictionary with fake data."""
        data = cls._build_data(**kwargs)
        return data

    @classmethod
    def _build_data(cls, **kwargs: Any) -> Dict[str, Any]:
        """Build the data dictionary. Override in subclasses."""
        return {}


class UserFactory(BaseFactory):
    """Factory for creating user data."""

    @classmethod
    def _build_data(cls, **kwargs: Any) -> Dict[str, Any]:
        """Build user data."""
        data = {
            "email": fake.email(),
            "password": fake.password(length=12),
        }
        data.update(kwargs)
        return data


class DocumentFactory(BaseFactory):
    """Factory for creating document data."""

    @classmethod
    def _build_data(cls, **kwargs: Any) -> Dict[str, Any]:
        """Build document data."""
        data = {
            "filename": fake.file_name(extension="pdf"),
            "content_type": "application/pdf",
            "file_size": fake.pyint(min_value=100, max_value=10000000),
            "file_hash": fake.sha256(),
            "storage_url": f"https://storage.example.com/{uuid.uuid4()}.pdf",
            "user_id": str(uuid.uuid4()),
        }
        data.update(kwargs)
        return data


class ChatFactory(BaseFactory):
    """Factory for creating chat data."""

    @classmethod
    def _build_data(cls, **kwargs: Any) -> Dict[str, Any]:
        """Build chat data."""
        data = {
            "title": fake.sentence(nb_words=4),
            "user_id": str(uuid.uuid4()),
        }
        data.update(kwargs)
        return data


class MessageFactory(BaseFactory):
    """Factory for creating message data."""

    @classmethod
    def _build_data(cls, **kwargs: Any) -> Dict[str, Any]:
        """Build message data."""
        data = {
            "content": fake.paragraph(nb_sentences=3),
            "chat_id": str(uuid.uuid4()),
            "role": fake.random_element(elements=("user", "assistant")),
        }
        data.update(kwargs)
        return data


class DocumentChunkFactory(BaseFactory):
    """Factory for creating document chunk data."""

    @classmethod
    def _build_data(cls, **kwargs: Any) -> Dict[str, Any]:
        """Build document chunk data."""
        data = {
            "document_id": str(uuid.uuid4()),
            "content": fake.paragraph(nb_sentences=5),
            "chunk_index": fake.pyint(min_value=0, max_value=100),
            "word_count": fake.pyint(min_value=50, max_value=500),
        }
        data.update(kwargs)
        return data


class ProcessingTaskFactory(BaseFactory):
    """Factory for creating processing task data."""

    @classmethod
    def _build_data(cls, **kwargs: Any) -> Dict[str, Any]:
        """Build processing task data."""
        data = {
            "task_id": str(uuid.uuid4()),
            "document_id": str(uuid.uuid4()),
            "task_type": "process_document",
            "status": fake.random_element(
                elements=("PENDING", "PROCESSING", "COMPLETED", "FAILED")
            ),
            "created_at": datetime.utcnow(),
        }
        data.update(kwargs)
        return data


# Convenience functions
def create_user_data(**kwargs: Any) -> Dict[str, Any]:
    """Create user test data."""
    return UserFactory.create(**kwargs)


def create_document_data(**kwargs: Any) -> Dict[str, Any]:
    """Create document test data."""
    return DocumentFactory.create(**kwargs)


def create_chat_data(**kwargs: Any) -> Dict[str, Any]:
    """Create chat test data."""
    return ChatFactory.create(**kwargs)


def create_message_data(**kwargs: Any) -> Dict[str, Any]:
    """Create message test data."""
    return MessageFactory.create(**kwargs)


def create_document_chunk_data(**kwargs: Any) -> Dict[str, Any]:
    """Create document chunk test data."""
    return DocumentChunkFactory.create(**kwargs)


def create_processing_task_data(**kwargs: Any) -> Dict[str, Any]:
    """Create processing task test data."""
    return ProcessingTaskFactory.create(**kwargs)