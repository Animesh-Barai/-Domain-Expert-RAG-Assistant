"""CRUD operations for messages."""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate


class CRUDMessage:
    """CRUD operations for Message model."""

    async def get(self, db: AsyncSession, *, id: str) -> Optional[Message]:
        """Get message by ID."""
        result = await db.execute(
            select(Message)
            .options(selectinload(Message.chat))
            .filter(Message.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_chat(
        self,
        db: AsyncSession,
        *,
        chat_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get multiple messages by chat ID."""
        result = await db.execute(
            select(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Union[MessageCreate, Dict[str, Any]]) -> Message:
        """Create new message."""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict()

        db_obj = Message(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Message,
        obj_in: Union[MessageUpdate, Dict[str, Any]]
    ) -> Message:
        """Update message."""
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

    async def delete(self, db: AsyncSession, *, id: str) -> Message:
        """Delete message."""
        obj = await self.get(db, id=id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def count_by_chat(self, db: AsyncSession, *, chat_id: str) -> int:
        """Count messages by chat."""
        from sqlalchemy import func

        result = await db.execute(
            select(func.count(Message.id))
            .filter(Message.chat_id == chat_id)
        )
        return result.scalar()


# Create a singleton instance
message = CRUDMessage()