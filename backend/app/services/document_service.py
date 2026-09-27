import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from app.domain.document_status import DocumentStatus
from app.models.evidence import Document, Evidence
from app.providers.document_processing import DocumentProcessingProvider
from app.providers.document_storage import DocumentStorageProvider
from app.repositories.evidence import DocumentRepository
from app.ingestion.document_extraction import DocumentExtraction
from app.services.claim_validation import ClaimValidationService
from app.services.evidence_consistency import EvidenceConsistencyService


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        storage: DocumentStorageProvider,
        processor: DocumentProcessingProvider,
        claim_validator: ClaimValidationService | None = None,
    ):
        self.repository = repository
        self.storage = storage
        self.processor = processor
        self.claim_validator = claim_validator or ClaimValidationService()
        self.consistency = EvidenceConsistencyService()

    async def upload(
        self,
        citizen_id: UUID,
        document_type: str,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> tuple[Document, bool]:
        content_hash = hashlib.sha256(content).hexdigest()
        duplicate = await self.repository.find_by_hash(citizen_id, content_hash)
        if duplicate:
            return duplicate, True

        document_id = uuid.uuid4()
        storage_reference = await self.storage.store(document_id, filename, content)
        document = Document(
            id=document_id,
            citizen_id=citizen_id,
            document_type=document_type,
            file_url=storage_reference,
            storage_reference=storage_reference,
            content_hash=content_hash,
            status=DocumentStatus.UPLOADED.value,
            verification_status="PENDING",
            metadata_={"original_filename": filename, "content_type": content_type, "size_bytes": len(content)},
            extraction_method="PENDING",
            uploaded_at=datetime.now(timezone.utc),
        )
        try:
            await self.repository.create_document(document)
            await self.process_document(document)
        except Exception:
            await self.storage.delete(storage_reference)
            await self.repository.update_document(document, status=DocumentStatus.FAILED.value)
            raise
        return document, False

    async def process_document(self, document: Document) -> Document:
        document.status = DocumentStatus.PROCESSING.value
        await self.repository.session.flush()
        try:
            content = await self.storage.retrieve(document.storage_reference)
            filename = (document.metadata_ or {}).get("original_filename", "document")
            extraction = await self.processor.process(
                document.id, document.document_type, filename, content
            )
            await self._persist_extraction(document, extraction)
            return document
        except Exception:
            document.status = DocumentStatus.FAILED.value
            await self.repository.session.flush()
            raise

    async def _persist_extraction(self, document: Document, extraction: DocumentExtraction) -> None:
        document.extracted_data = {claim.field: claim.value for claim in extraction.claims}
        document.extraction_method = extraction.extraction_method
        document.processing_provider = extraction.provider or self.processor.provider_name
        document.processing_model = extraction.model or getattr(self.processor, "model_name", "")
        document.prompt_version = extraction.prompt_version or self.processor.prompt_version
        document.processed_at = datetime.now(timezone.utc)
        document.status = DocumentStatus.EXTRACTED.value
        for claim in extraction.claims:
            if self.claim_validator.validate(claim):
                evidence_status = (
                    self.claim_validator.evidence_status(claim)
                    if extraction.provider == "GEMINI"
                    else "PENDING"
                )
                self.repository.session.add(Evidence(
                    citizen_id=document.citizen_id,
                    document_id=document.id,
                    evidence_type=claim.field,
                    claim_type=claim.field,
                    claim_value={"value": claim.value, "source_location": claim.source_location, "extraction_method": claim.extraction_method},
                    data={claim.field: claim.value},
                    confidence=claim.confidence,
                    verification_status=evidence_status,
                    provenance={
                        "source_location": claim.source_location,
                        "source_reference": claim.source_reference,
                        "extraction_method": claim.extraction_method,
                    },
                ))
        if extraction.provider == "GEMINI" and any(claim.confidence != "HIGH" for claim in extraction.claims):
            document.status = DocumentStatus.NEEDS_REVIEW.value
        elif extraction.provider == "GEMINI":
            document.status = "EVIDENCE_GENERATED"
        else:
            # Preserve the Phase 6A mock response contract while evidence is generated.
            document.status = DocumentStatus.EXTRACTED.value
        await self.repository.session.flush()
