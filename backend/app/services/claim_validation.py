from app.ingestion.document_extraction import DocumentClaim

VALID_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


class ClaimValidationService:
    """Validates extracted claims before they become evidence."""

    def validate(self, claim: DocumentClaim) -> bool:
        if claim.confidence not in VALID_CONFIDENCE:
            return False
        if not claim.field or claim.value is None:
            return False
        return True

    def evidence_status(self, claim: DocumentClaim) -> str:
        return "CANDIDATE" if claim.confidence == "HIGH" else "NEEDS_REVIEW"
