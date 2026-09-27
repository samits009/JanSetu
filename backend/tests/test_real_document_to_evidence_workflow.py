import pytest
from app.db.seed import RAMESH_UUID
from app.models.evidence import Evidence
from app.providers.document_processing import DocumentProcessingProvider
from app.providers.document_storage import LocalDocumentStorageProvider
from app.repositories.evidence import DocumentRepository
from app.services.document_service import DocumentService
from app.ingestion.document_extraction import DocumentExtraction, DocumentClaim


class MockedGeminiProvider(DocumentProcessingProvider):
    provider_name = "GEMINI"
    model_name = "mock-gemini"
    prompt_version = "document_extraction_v1"

    async def process(self, document_id, document_type, filename, content):
        return DocumentExtraction(
            claims=[DocumentClaim(
                field="occupation", value="Construction Worker", confidence="HIGH",
                source_location="page 1 header", extraction_method="GEMINI", source_reference="page:1"
            )],
            extraction_method="GEMINI", provider="GEMINI", model="mock-gemini", prompt_version="document_extraction_v1"
        )


@pytest.mark.asyncio
async def test_real_document_to_evidence_workflow(db_session, tmp_path):
    service = DocumentService(
        DocumentRepository(db_session),
        LocalDocumentStorageProvider(str(tmp_path)),
        MockedGeminiProvider(),
    )
    document, duplicate = await service.upload(
        RAMESH_UUID, "BOCW_CARD", "worker.pdf", "application/pdf", b"worker certificate"
    )
    from sqlalchemy import select
    evidence = (await db_session.execute(select(Evidence).where(Evidence.document_id == document.id))).scalars().first()
    assert duplicate is False
    assert document.content_hash
    assert document.processing_provider == "GEMINI"
    assert document.processing_model == "mock-gemini"
    assert evidence is not None
    assert evidence.claim_type == "occupation"
    assert evidence.provenance["source_reference"] == "page:1"
