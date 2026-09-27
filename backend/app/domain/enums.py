import enum

class ApplicationStatus(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    ELIGIBILITY_CHECKED = "ELIGIBILITY_CHECKED"
    EVIDENCE_REQUIRED = "EVIDENCE_REQUIRED"
    EVIDENCE_COMPLETE = "EVIDENCE_COMPLETE"
    DRAFTED = "DRAFTED"
    AWAITING_CONSENT = "AWAITING_CONSENT"
    SUBMITTING = "SUBMITTING"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REQUIRES_EVIDENCE = "REQUIRES_EVIDENCE"
    REJECTED = "REJECTED"
    RECOVERY_READY = "RECOVERY_READY"
    RESUBMITTED = "RESUBMITTED"
    APPROVED = "APPROVED"
    FAILED = "FAILED"

class EligibilityStatus(str, enum.Enum):
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    UNKNOWN = "unknown"

class ConfidenceLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class BenefitStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    PORTABLE = "PORTABLE"
    LOST = "LOST"

class ConsentAction(str, enum.Enum):
    DOCUMENT_PROCESSING = "DOCUMENT_PROCESSING"
    APPLICATION_SUBMISSION = "APPLICATION_SUBMISSION"
    APPLICATION_RESUBMISSION = "APPLICATION_RESUBMISSION"

class SchemeCategory(str, enum.Enum):
    HEALTH = "HEALTH"
    HOUSING = "HOUSING"
    PENSION = "PENSION"
    EMPLOYMENT = "EMPLOYMENT"
    EDUCATION = "EDUCATION"
    NUTRITION = "NUTRITION"

class VerificationStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    DEMO = "DEMO"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    STALE = "STALE"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"

class SourceType(str, enum.Enum):
    HTML = "HTML"
    PDF = "PDF"
    JSON = "JSON"
    API = "API"
    PORTAL = "PORTAL"
    FIXTURE = "FIXTURE"

class JurisdictionLevel(str, enum.Enum):
    CENTRAL = "CENTRAL"
    STATE = "STATE"
    DISTRICT = "DISTRICT"
    LOCAL = "LOCAL"

class PortabilityState(str, enum.Enum):
    PORTABLE = "PORTABLE"
    NON_PORTABLE = "NON_PORTABLE"
    CONDITIONALLY_PORTABLE = "CONDITIONALLY_PORTABLE"
    UNKNOWN = "UNKNOWN"

class ExtractionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
