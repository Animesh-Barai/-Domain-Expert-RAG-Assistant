"""Chat endpoints with streaming support."""

import json
from typing import Any, Generator, List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.chat import Chat
from app.models.message import Message, MessageRole
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatResponse, ChatUpdate
from app.schemas.message import MessageCreate, MessageResponse
from app.services.rag_service import RAGService

router = APIRouter()
# Initialized inside endpoints to avoid startup circularity


@router.post(
    "/", 
    response_model=ChatResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))]
)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new chat session."""
    from app.crud.chat import chat as chat_crud

    chat = await chat_crud.create(db, obj_in={**chat_data.dict(), "user_id": current_user.id})
    return chat


@router.get("/", response_model=List[ChatResponse])
async def list_chats(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List user's chat sessions."""
    from app.crud.chat import chat as chat_crud

    chats = await chat_crud.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return chats


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get chat session by ID."""
    from app.crud.chat import chat as chat_crud

    chat = await chat_crud.get_user_chat(
        db, id=chat_id, user_id=current_user.id
    )
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session."""
    from app.crud.chat import chat as chat_crud

    chat = await chat_crud.get_user_chat(
        db, id=chat_id, user_id=current_user.id
    )
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    await chat_crud.delete(db, id=chat_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{chat_id}/messages", 
    response_model=MessageResponse,
    dependencies=[Depends(RateLimiter(times=20, minutes=1))]
)
async def send_message(
    chat_id: str,
    message_data: MessageCreate,
    stream: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Send a message and get AI response."""
    from app.services.rag_service import RAGService
    rag_service = RAGService()
    from app.crud.chat import chat as chat_crud
    from app.crud.message import message as message_crud

    # Verify chat exists and belongs to user
    chat = await chat_crud.get_user_chat(
        db, id=chat_id, user_id=current_user.id
    )
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    # Create user message
    user_message = await message_crud.create(
        db,
        obj_in={
            **message_data.dict(),
            "chat_id": chat_id,
            "role": MessageRole.USER,
        }
    )

    if stream:
        return StreamingResponse(
            stream_chat_response(chat_id, user_message.id, message_data.content, current_user.id),
            media_type="text/plain"
        )
    else:
        response_content = ""
        async for item in rag_service.stream_response(
            message=message_data.content,
            user_id=current_user.id,
            chat_id=chat_id,
        ):
            if isinstance(item, str):
                response_content += item

        assistant_message = await message_crud.create(
            db,
            obj_in={
                "content": response_content,
                "chat_id": chat_id,
                "role": MessageRole.ASSISTANT,
            }
        )

        return assistant_message


async def stream_chat_response(
    chat_id: str,
    user_message_id: str,
    user_content: str,
    user_id: str
) -> Generator[str, None, None]:
    """Stream chat response chunk by chunk."""
    from app.core.database import get_async_session
    from app.crud.message import message as message_crud

    response_content = ""

    try:
        from app.services.rag_service import RAGService
        rag_service = RAGService()
        async for item in rag_service.stream_response(
            message=user_content,
            user_id=user_id,
            chat_id=chat_id,
        ):
            if isinstance(item, dict):
                # Send metadata packet
                yield f"data: {json.dumps(item)}\n\n"
            else:
                response_content += item
                # Send text chunk packet
                yield f"data: {json.dumps({'chunk': item})}\n\n"

        # Save complete message to database
        async with get_async_session() as db:
            await message_crud.create(
                db,
                obj_in={
                    "content": response_content,
                    "chat_id": chat_id,
                    "role": MessageRole.ASSISTANT,
                }
            )
            await db.commit()

    except Exception as e:
        import traceback
        error_msg = f"Error in stream_chat_response: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        yield f"data: {json.dumps({'error': error_msg})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    chat_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List messages in a chat."""
    from app.crud.chat import chat as chat_crud
    from app.crud.message import message as message_crud

    chat = await chat_crud.get_user_chat(
        db, id=chat_id, user_id=current_user.id
    )
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    messages = await message_crud.get_multi_by_chat(
        db, chat_id=chat_id, skip=skip, limit=limit
    )
    return messages