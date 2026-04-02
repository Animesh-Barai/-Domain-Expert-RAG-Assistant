"""CRUD operations for documents."""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


class CRUDDocument:
    """CRUD operations for Document model."""

    async def get(self, db: AsyncSession, *, id: str) -> Optional[Document]:
        """Get document by ID."""
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.user))
            .filter(Document.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_hash(self, db: AsyncSession, *, hash: str) -> Optional[Document]:
        """Get document by file hash."""
        result = await db.execute(
            select(Document)
            .filter(Document.file_hash == hash)
        )
        return result.scalar_one_or_none()

    async def get_user_document(
        self, db: AsyncSession, *, id: str, user_id: str
    ) -> Optional[Document]:
        """Get document by ID and user ID."""
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.user))
            .filter(Document.id == id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """Get multiple documents by user ID."""
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.user))
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: DocumentCreate) -> Document:
        """Create new document."""
        db_obj = Document(
            filename=obj_in.filename,
            file_hash=obj_in.file_hash,
            file_size=obj_in.file_size,
            content_type=obj_in.content_type,
            storage_url=obj_in.storage_url,
            user_id=obj_in.user_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Document,
        obj_in: Union[DocumentUpdate, Dict[str, Any]]
    ) -> Document:
        """Update document."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: str) -> Document:
        """Delete document."""
        obj = await self.get(db, id=id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def count_by_user(self, db: AsyncSession, *, user_id: str) -> int:
        """Count documents by user."""
        from sqlalchemy import func

        result = await db.execute(
            select(func.count(Document.id))
            .filter(Document.user_id == user_id)
        )
        return result.scalar()


# Create a singleton instance
document = CRUDDocument()