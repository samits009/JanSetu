from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request, Response
from typing import List, Optional
from uuid import UUID
from pathlib import Path
import re
import os

from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.evidence import DocumentRepository
from app.providers.document_processing import MockDocumentProcessingProvider, GeminiDocumentProcessingProvider
from app.providers.document_storage import get_document_storage_provider
from app.services.document_service import DocumentService

from app.schemas.document import DocumentResponse, DocumentDetailResponse, DocumentUploadResponse, EvidenceResponse
from app.services.authorization import authorize_citizen
from app.services.authentication import AuthenticationService

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def _safe_filename(filename: str) -> str:
    name = Path(filename or "document").name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name[:120] or "document"


def get_document_service(db: AsyncSession = Depends(get_async_db)) -> DocumentService:
    gemini = GeminiDocumentProcessingProvider()
    processor = gemini if gemini.available else MockDocumentProcessingProvider()
    return DocumentService(
        DocumentRepository(db),
        get_document_storage_provider(),
        processor,
    )


@router.post("/", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    document_type: str = Form(..., min_length=1, max_length=80),
    file: UploadFile = File(...),
    citizen_id: Optional[UUID] = Form(None),
    service: DocumentService = Depends(get_document_service),
):
    """Upload a document for the authenticated citizen context."""
    if citizen_id:
        principal = await authorize_citizen(citizen_id, request, service.repository.session)
        effective_citizen_id = principal.citizen_id
    else:
        principal = await AuthenticationService(service.repository.session).current(request)
        if not principal.citizen_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        effective_citizen_id = principal.citizen_id

    filename = _safe_filename(file.filename or "document")
    extension = Path(filename).suffix.lower()
    expected_mime = ALLOWED_TYPES.get(extension)
    if not expected_mime or file.content_type != expected_mime:
        raise HTTPException(status_code=415, detail="Unsupported document type")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Document exceeds the 10 MB limit")

    document, duplicate = await service.upload(
        citizen_id=effective_citizen_id,
        document_type=document_type.strip().upper(),
        filename=filename,
        content_type=file.content_type,
        content=content,
    )
    return DocumentUploadResponse(
        document_id=document.id,
        status=document.status,
        document_type=document.document_type,
        uploaded_at=document.uploaded_at,
        duplicate_detected=duplicate,
    )

# Note: this provides an alternative global entry point for documents.
# The citizen route also provides /api/citizens/{citizen_id}/documents

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    request: Request, 
    citizen_id: Optional[UUID] = None, 
    db: AsyncSession = Depends(get_async_db)
):
    if citizen_id:
        principal = await authorize_citizen(citizen_id, request, db)
        effective_citizen_id = principal.citizen_id
    else:
        principal = await AuthenticationService(db).current(request)
        if not principal.citizen_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        effective_citizen_id = principal.citizen_id

    repo = DocumentRepository(db)
    docs = await repo.find_for_citizen(effective_citizen_id)
    return docs


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: UUID, 
    request: Request, 
    citizen_id: Optional[UUID] = None, 
    db: AsyncSession = Depends(get_async_db)
):
    if citizen_id:
        principal = await authorize_citizen(citizen_id, request, db)
        effective_citizen_id = principal.citizen_id
    else:
        principal = await AuthenticationService(db).current(request)
        if not principal.citizen_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        effective_citizen_id = principal.citizen_id

    document = await DocumentRepository(db).get_detail_for_citizen(document_id, effective_citizen_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": document.id,
        "document_type": document.document_type,
        "document_number": document.document_number,
        "status": document.status,
        "verification_status": document.verification_status,
        "storage_reference": document.storage_reference,
        "content_hash": document.content_hash,
        "uploaded_at": document.uploaded_at,
        "processed_at": document.processed_at,
        "expires_at": document.expires_at,
        "metadata": document.metadata_ or {},
        "extraction_method": document.extraction_method,
        "processing_provider": document.processing_provider,
        "processing_model": document.processing_model,
        "prompt_version": document.prompt_version,
        "extracted_data": document.extracted_data or {},
        "evidence": document.evidence,
    }


@router.get("/{document_id}/download")
@router.get("/{document_id}/content")
async def download_document(
    document_id: UUID,
    request: Request,
    citizen_id: Optional[UUID] = None,
    service: DocumentService = Depends(get_document_service),
):
    if citizen_id:
        principal = await authorize_citizen(citizen_id, request, service.repository.session)
        effective_citizen_id = principal.citizen_id
    else:
        principal = await AuthenticationService(service.repository.session).current(request)
        if not principal.citizen_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        effective_citizen_id = principal.citizen_id

    document = await service.repository.get_detail_for_citizen(document_id, effective_citizen_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    content = await service.storage.retrieve(document.storage_reference)
    meta = document.metadata_ or {}
    mime_type = meta.get("content_type", "application/octet-stream")
    filename = meta.get("original_filename", f"{document.id}.bin")

    return Response(
        content=content,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-SHA256": document.content_hash,
            "Content-Length": str(len(content)),
        },
    )


@router.post("/{document_id}/process", response_model=DocumentUploadResponse)
async def process_document(
    document_id: UUID,
    request: Request,
    citizen_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_async_db),
):
    if citizen_id:
        principal = await authorize_citizen(citizen_id, request, db)
        effective_citizen_id = principal.citizen_id
    else:
        principal = await AuthenticationService(db).current(request)
        if not principal.citizen_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        effective_citizen_id = principal.citizen_id

    document = await DocumentRepository(db).get_detail_for_citizen(document_id, effective_citizen_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    service = get_document_service(db)
    await service.process_document(document)
    return DocumentUploadResponse(
        document_id=document.id,
        status=document.status,
        document_type=document.document_type,
        uploaded_at=document.uploaded_at,
        duplicate_detected=False,
    )


@router.get("/{document_id}/claims", response_model=List[EvidenceResponse])
async def get_document_claims(
    document_id: UUID,
    request: Request,
    citizen_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_async_db),
):
    if citizen_id:
        principal = await authorize_citizen(citizen_id, request, db)
        effective_citizen_id = principal.citizen_id
    else:
        principal = await AuthenticationService(db).current(request)
        if not principal.citizen_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        effective_citizen_id = principal.citizen_id

    document = await DocumentRepository(db).get_detail_for_citizen(document_id, effective_citizen_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.evidence
