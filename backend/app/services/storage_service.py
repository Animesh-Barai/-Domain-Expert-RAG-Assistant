"""Storage service for MinIO S3."""

import os
import uuid
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

settings = get_settings()


class StorageService:
    """Service for handling file storage with MinIO."""

    def __init__(self):
        """Initialize MinIO client."""
        # Extract host:port from endpoint URL
        endpoint_url = settings.get_s3_endpoint_url()
        if endpoint_url.startswith("http://"):
            endpoint = endpoint_url[7:]  # Remove http://
        elif endpoint_url.startswith("https://"):
            endpoint = endpoint_url[8:]  # Remove https://
        else:
            endpoint = endpoint_url

        self.client = Minio(
            endpoint=endpoint,
            access_key=settings.get_aws_access_key_id(),
            secret_key=settings.get_aws_secret_access_key(),
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    async def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise Exception(f"Failed to create bucket: {e}")

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None,
    ) -> str:
        """Upload a file to MinIO storage."""
        await self._ensure_bucket_exists()

        # Generate unique object name
        file_extension = os.path.splitext(filename)[1]
        object_name = f"documents/{uuid.uuid4()}{file_extension}"

        try:
            # Upload file
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_content,
                length=len(file_content),
                content_type=content_type or "application/octet-stream",
            )

            # Return URL
            return f"{settings.get_s3_endpoint_url()}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            raise Exception(f"Failed to upload file: {e}")

    async def download_file(self, storage_url: str) -> bytes:
        """Download a file from MinIO storage."""
        # Extract object name from URL
        # URL format: http://localhost:9000/bucket-name/documents/uuid.pdf
        parts = storage_url.split("/")
        if len(parts) < 4:
            raise ValueError("Invalid storage URL format")

        bucket_name = parts[3]
        object_name = "/".join(parts[4:])

        try:
            response = self.client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error as e:
            raise Exception(f"Failed to download file: {e}")
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

    async def delete_file(self, storage_url: str) -> None:
        """Delete a file from MinIO storage."""
        # Extract object name from URL
        parts = storage_url.split("/")
        if len(parts) < 4:
            raise ValueError("Invalid storage URL format")

        bucket_name = parts[3]
        object_name = "/".join(parts[4:])

        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            raise Exception(f"Failed to delete file: {e}")

    async def get_file_metadata(self, storage_url: str) -> dict:
        """Get file metadata from MinIO storage."""
        # Extract object name from URL
        parts = storage_url.split("/")
        if len(parts) < 4:
            raise ValueError("Invalid storage URL format")

        bucket_name = parts[3]
        object_name = "/".join(parts[4:])

        try:
            stat = self.client.stat_object(bucket_name, object_name)
            return {
                "content_type": stat.content_type,
                "size": stat.size,
                "last_modified": stat.last_modified.isoformat(),
                "etag": stat.etag,
            }
        except S3Error as e:
            raise Exception(f"Failed to get file metadata: {e}")