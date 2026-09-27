import pytest
from uuid import uuid4
from app.providers.document_processing import MockDocumentProcessingProvider
from app.providers.document_storage import LocalDocumentStorageProvider
from app.services.document_service import DocumentService
from app.repositories.evidence import DocumentRepository
from app.ingestion.document_extraction import DocumentExtraction
from app.db.seed import RAMESH_UUID


@pytest.mark.asyncio
async def test_mock_processing_is_explicit_and_structured():
    extraction = await MockDocumentProcessingProvider().process(
        uuid4(), "GENERAL", "proof.pdf", b"content"
    )
    assert extraction.extraction_method == "MOCK"
    assert extraction.claims[0].extraction_method == "MOCK"
    assert extraction.claims[0].source_location == "mock-provider"


class FailingDocumentProcessor:
    async def process(self, document_id, document_type, filename, content):
        raise RuntimeError("processing failed")


@pytest.mark.asyncio
async def test_processing_failure_marks_document_failed_and_cleans_storage(db_session, tmp_path):
    service = DocumentService(
        DocumentRepository(db_session),
        LocalDocumentStorageProvider(str(tmp_path)),
        FailingDocumentProcessor(),
    )
    with pytest.raises(RuntimeError, match="processing failed"):
        await service.upload(RAMESH_UUID, "GENERAL", "failed.pdf", "application/pdf", b"failed")

    document = await DocumentRepository(db_session).find_by_hash(
        RAMESH_UUID, __import__("hashlib").sha256(b"failed").hexdigest()
    )
    assert document is not None
    assert document.status == "FAILED"
    assert not (tmp_path / document.storage_reference).exists()
