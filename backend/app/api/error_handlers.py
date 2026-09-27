from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import (
    DomainException,
    CitizenNotFoundError,
    SchemeNotFoundError,
    ApplicationNotFoundError,
    ConsentRequiredError,
    InvalidApplicationTransitionError,
    ProviderError
)
from app.schemas.common import ErrorResponse

async def domain_exception_handler(request: Request, exc: DomainException):
    # Default mapping
    status_code = 400
    error_code = "DOMAIN_ERROR"
    retryable = False

    if isinstance(exc, CitizenNotFoundError):
        status_code = 404
        error_code = "CITIZEN_NOT_FOUND"
    elif isinstance(exc, SchemeNotFoundError):
        status_code = 404
        error_code = "SCHEME_NOT_FOUND"
    elif isinstance(exc, ApplicationNotFoundError):
        status_code = 404
        error_code = "APPLICATION_NOT_FOUND"
    elif isinstance(exc, ConsentRequiredError):
        status_code = 403
        error_code = "CONSENT_REQUIRED"
    elif isinstance(exc, InvalidApplicationTransitionError):
        status_code = 409
        error_code = "INVALID_TRANSITION"
    elif isinstance(exc, ProviderError):
        status_code = 502
        error_code = "PROVIDER_ERROR"
        retryable = True

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error_code=error_code,
            message=str(exc),
            retryable=retryable
        ).model_dump()
    )

def register_exception_handlers(app):
    app.add_exception_handler(DomainException, domain_exception_handler)
