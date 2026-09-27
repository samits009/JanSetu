from app.ingestion.models import SchemeExtractionResult
from app.domain.enums import VerificationStatus, SourceType

class Validator:
    """
    Validates a normalized extraction result against strict domain rules.
    Decides the VerificationStatus.
    """
    def validate(self, extracted: SchemeExtractionResult) -> VerificationStatus:
        # Check mandatory fields
        if not extracted.official_name or not extracted.category:
            return VerificationStatus.REJECTED
            
        # Provenance-based validation
        if extracted.source_type == SourceType.FIXTURE:
            # Deterministic extraction proves it was parsed correctly, but not legally verified
            return VerificationStatus.DEMO
            
        if extracted.needs_human_review or extracted.confidence_score < 0.9:
            return VerificationStatus.NEEDS_REVIEW
            
        # In the future, Authoritative government source independently checked -> VERIFIED
        # Stale source -> STALE
        
        return VerificationStatus.UNKNOWN
