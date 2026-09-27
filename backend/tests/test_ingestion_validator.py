import pytest
from app.ingestion.validator import Validator
from app.ingestion.models import SchemeExtractionResult
from app.domain.enums import VerificationStatus, SourceType, PortabilityState

def test_validator_fixture_is_demo():
    validator = Validator()
    extracted = SchemeExtractionResult(
        official_name="Test Scheme",
        category="EMPLOYMENT",
        description="A test scheme",
        source_type=SourceType.FIXTURE,
        portability=PortabilityState.NON_PORTABLE
    )
    status = validator.validate(extracted)
    assert status == VerificationStatus.DEMO

def test_validator_needs_review():
    validator = Validator()
    extracted = SchemeExtractionResult(
        official_name="Test Scheme",
        category="EMPLOYMENT",
        description="A test scheme",
        source_type=SourceType.HTML, # AI extraction
        needs_human_review=True,
        portability=PortabilityState.NON_PORTABLE
    )
    status = validator.validate(extracted)
    assert status == VerificationStatus.NEEDS_REVIEW

def test_validator_low_confidence():
    validator = Validator()
    extracted = SchemeExtractionResult(
        official_name="Test Scheme",
        category="EMPLOYMENT",
        description="A test scheme",
        source_type=SourceType.HTML,
        confidence_score=0.5,
        portability=PortabilityState.NON_PORTABLE
    )
    status = validator.validate(extracted)
    assert status == VerificationStatus.NEEDS_REVIEW

def test_validator_missing_fields_rejected():
    validator = Validator()
    extracted = SchemeExtractionResult(
        official_name="",
        category="EMPLOYMENT",
        description="A test scheme",
        source_type=SourceType.HTML,
        portability=PortabilityState.NON_PORTABLE
    )
    status = validator.validate(extracted)
    assert status == VerificationStatus.REJECTED
