"""Test configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import get_async_session
from app.main import app
from app.models.base import Base

settings = get_settings()

# Test database URL
TEST_DATABASE_URL = settings.get_database_url().replace(
    f"/{settings.DB_NAME}", f"/{settings.DB_NAME}_test"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def test_client(test_db_session: AsyncSession) -> TestClient:
    """Create a test client with database dependency override."""
    app.dependency_overrides[get_async_session] = lambda: test_db_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    app.dependency_overrides[get_async_session] = lambda: test_db_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_password():
    """Test password fixture."""
    return "TestPassword123!"


@pytest.fixture
def test_user_data():
    """Test user data fixture."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
    }


@pytest.fixture
async def test_user(test_db_session: AsyncSession, test_user_data: dict):
    """Create a test user."""
    from app.crud.user import user as user_crud
    from app.schemas.auth import UserCreate

    user_in = UserCreate(
        email=test_user_data["email"],
        password=test_user_data["password"]
    )
    user = await user_crud.create(test_db_session, obj_in=user_in)
    return user


@pytest.fixture
async def test_user_token(test_user):
    """Create a test JWT token for the test user."""
    from app.core.security import create_access_token

    access_token = create_access_token(subject=test_user.id)
    return access_token


@pytest.fixture
def test_headers(test_user_token: str):
    """Create test headers with JWT token."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def sample_pdf_content():
    """Sample PDF file content for testing."""
    # This would be actual PDF bytes in a real implementation
    # For now, return dummy content
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"


@pytest.fixture
def sample_text():
    """Sample text content for testing."""
    return """
    This is a sample document for testing purposes.
    It contains multiple sentences and paragraphs.
    The text should be long enough to test chunking functionality.
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco.
    Duis aute irure dolor in reprehenderit in voluptate velit esse.
    Excepteur sint occaecat cupidatat non proident sunt in culpa.
    """


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "filename": "test_document.pdf",
        "content_type": "application/pdf",
        "file_size": 1024,
        "file_hash": "abc123def456",
    }


@pytest.fixture
async def test_document(test_db_session: AsyncSession, test_user, sample_document_data: dict):
    """Create a test document."""
    from app.crud.document import document as document_crud
    from app.schemas.document import DocumentCreate

    doc_in = DocumentCreate(
        **sample_document_data,
        storage_url="http://test.com/test.pdf",
        user_id=test_user.id
    )
    document = await document_crud.create(test_db_session, obj_in=doc_in)
    return document


@pytest.fixture
async def test_chat(test_db_session: AsyncSession, test_user):
    """Create a test chat."""
    from app.crud.chat import chat as chat_crud
    from app.schemas.chat import ChatCreate

    chat_in = ChatCreate(title="Test Chat")
    chat = await chat_crud.create(
        test_db_session,
        obj_in={**chat_in.dict(), "user_id": test_user.id}
    )
    return chat


# Markers for different test types
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
pytest.mark.external = pytest.mark.external