"""CRUD operations for chats."""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Chat
from app.schemas.chat import ChatCreate, ChatUpdate


class CRUDChat:
    """CRUD operations for Chat model."""

    async def get(self, db: AsyncSession, *, id: str) -> Optional[Chat]:
        """Get chat by ID."""
        result = await db.execute(
            select(Chat)
            .options(selectinload(Chat.user), selectinload(Chat.messages))
            .filter(Chat.id == id)
        )
        return result.scalar_one_or_none()

    async def get_user_chat(
        self, db: AsyncSession, *, id: str, user_id: str
    ) -> Optional[Chat]:
        """Get chat by ID and user ID."""
        result = await db.execute(
            select(Chat)
            .options(selectinload(Chat.user), selectinload(Chat.messages))
            .filter(Chat.id == id, Chat.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Chat]:
        """Get multiple chats by user ID."""
        result = await db.execute(
            select(Chat)
            .options(selectinload(Chat.user))
            .filter(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Union[ChatCreate, Dict[str, Any]]) -> Chat:
        """Create new chat."""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict()

        db_obj = Chat(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Chat,
        obj_in: Union[ChatUpdate, Dict[str, Any]]
    ) -> Chat:
        """Update chat."""
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

    async def delete(self, db: AsyncSession, *, id: str) -> Chat:
        """Delete chat."""
        obj = await self.get(db, id=id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def count_by_user(self, db: AsyncSession, *, user_id: str) -> int:
        """Count chats by user."""
        from sqlalchemy import func

        result = await db.execute(
            select(func.count(Chat.id))
            .filter(Chat.user_id == user_id)
        )
        return result.scalar()


# Create a singleton instance
chat = CRUDChat()