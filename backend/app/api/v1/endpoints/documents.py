"""Document management endpoints."""

import hashlib
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService

router = APIRouter()
document_service = DocumentService()
storage_service = StorageService()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Upload a new document."""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Read file content and calculate hash
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # Check if document already exists
    from app.crud.document import document as document_crud
    existing_doc = await document_crud.get_by_hash(db, hash=file_hash)
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document already exists"
        )

    # Upload to storage
    try:
        storage_url = await storage_service.upload_file(
            file_content=content,
            filename=file.filename,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

    # Create document record
    document_data = DocumentCreate(
        filename=file.filename,
        file_hash=file_hash,
        file_size=len(content),
        content_type=file.content_type,
        storage_url=storage_url,
        user_id=current_user.id,
    )

    document = await document_crud.create(db, obj_in=document_data)

    # Queue for processing
    try:
        await document_service.queue_for_processing(document.id)
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Failed to queue document for processing: {e}")

    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List user's documents."""
    from app.crud.document import document as document_crud

    documents = await document_crud.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get document by ID."""
    from app.crud.document import document as document_crud

    document = await document_crud.get_user_document(
        db, id=document_id, user_id=current_user.id
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete a document."""
    from app.crud.document import document as document_crud

    document = await document_crud.get_user_document(
        db, id=document_id, user_id=current_user.id
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete from storage
    if document.storage_url:
        try:
            await storage_service.delete_file(document.storage_url)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Failed to delete file from storage: {e}")

    # Delete from database
    await document_crud.delete(db, id=document_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{document_id}/process", response_model=DocumentResponse)
async def process_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Manually trigger document processing."""
    from app.crud.document import document as document_crud

    document = await document_crud.get_user_document(
        db, id=document_id, user_id=current_user.id
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if document.status == DocumentStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is already being processed"
        )

    try:
        await document_service.queue_for_processing(document_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue document for processing: {str(e)}"
        )

    # Update status to pending
    document_update = DocumentUpdate(status=DocumentStatus.PENDING)
    document = await document_crud.update(db, db_obj=document, obj_in=document_update)

    return document