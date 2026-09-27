class DomainException(Exception):
    """Base class for domain exceptions."""
    pass

class CitizenNotFoundError(DomainException):
    pass

class SchemeNotFoundError(DomainException):
    pass

class BenefitNotFoundError(DomainException):
    pass

class EvidenceMissingError(DomainException):
    pass

class EligibilityUnknownError(DomainException):
    pass

class InvalidApplicationTransitionError(DomainException):
    pass

class ConsentRequiredError(DomainException):
    pass

class ApplicationNotFoundError(DomainException):
    pass

class ProviderError(DomainException):
    pass
