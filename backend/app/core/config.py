"""Application configuration settings."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "rag_user"
    DB_PASSWORD: str = "rag_password"
    DB_NAME: str = "rag_db"
    DATABASE_URL: Optional[str] = None

    def get_database_url(self) -> str:
        """Construct database URL from components."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None

    def get_redis_url(self) -> str:
        """Construct Redis URL from components."""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # MinIO S3
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_CONSOLE_PORT: int = 9001
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "rag-documents"
    MINIO_SECURE: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    def get_s3_endpoint_url(self) -> str:
        """Construct S3 endpoint URL from components."""
        if self.S3_ENDPOINT_URL:
            return self.S3_ENDPOINT_URL
        return f"http://{self.MINIO_HOST}:{self.MINIO_PORT}"

    def get_aws_access_key_id(self) -> str:
        """Get AWS access key from MinIO root user."""
        if self.AWS_ACCESS_KEY_ID:
            return self.AWS_ACCESS_KEY_ID
        return self.MINIO_ROOT_USER

    def get_aws_secret_access_key(self) -> str:
        """Get AWS secret key from MinIO root password."""
        if self.AWS_SECRET_ACCESS_KEY:
            return self.AWS_SECRET_ACCESS_KEY
        return self.MINIO_ROOT_PASSWORD

    # Pinecone
    PINECONE_API_KEY: str = "dev-pinecone-key-change-in-production"
    PINECONE_INDEX_NAME: str = "rag-index"
    PINECONE_DIMENSION: int = 768
    PINECONE_METRIC: str = "cosine"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-west-2"

    # Google Gemini
    GEMINI_API_KEY: str = "dev-gemini-key-change-in-production"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_CHAT_MODEL: str = "gemini-1.5-flash"

    # Cohere (for reranking)
    COHERE_API_KEY: str = "dev-cohere-key-change-in-production"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 50
    RATE_LIMIT_PER_HOUR: int = 1000

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = "application/pdf"

    # RAG Configuration
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K_DENSE: int = 20
    TOP_K_SPARSE: int = 20
    TOP_K_RERANK: int = 5

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    def get_celery_broker_url(self) -> str:
        """Construct Celery broker URL from Redis URL."""
        if self.CELERY_BROKER_URL:
            return self.CELERY_BROKER_URL
        return self.get_redis_url()

    def get_celery_result_backend(self) -> str:
        """Construct Celery result backend URL from Redis URL."""
        if self.CELERY_RESULT_BACKEND:
            return self.CELERY_RESULT_BACKEND
        return self.get_redis_url()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()