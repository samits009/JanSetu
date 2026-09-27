from app.ingestion.document_extraction import DocumentClaim
from app.services.claim_validation import ClaimValidationService


def test_high_confidence_claim_is_candidate():
    claim = DocumentClaim(field="name", value="Ramesh Kumar", confidence="HIGH", source_location="page 1", extraction_method="GEMINI")
    service = ClaimValidationService()
    assert service.validate(claim)
    assert service.evidence_status(claim) == "CANDIDATE"


def test_medium_and_low_confidence_need_review():
    service = ClaimValidationService()
    for confidence in ("MEDIUM", "LOW"):
        claim = DocumentClaim(field="name", value="unclear", confidence=confidence, source_location="page 1", extraction_method="GEMINI")
        assert service.evidence_status(claim) == "NEEDS_REVIEW"
