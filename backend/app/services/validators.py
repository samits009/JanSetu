import re
from fastapi import HTTPException, status

# General RFC-compliant email regex:
# Accepts any legitimate domain (e.g. .com, .in, .ac.in, .org, .co.uk, .gov.in, etc.)
# Does NOT whitelist or restrict domain names.
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)

# Indian mobile regex (10 digits starting with 6, 7, 8, 9)
INDIAN_MOBILE_10_REGEX = re.compile(r"^[6-9]\d{9}$")


def is_email(identifier: str) -> bool:
    """Returns True if the identifier appears to be an email address."""
    return "@" in identifier


def normalize_and_validate_email(email: str) -> str:
    """
    Validates and normalizes an email address.
    - Strips leading/trailing whitespace
    - Validates syntax without restricting to a hardcoded domain whitelist
    - Preserves canonical lowercased representation
    """
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is required",
        )

    normalized = email.strip()
    # Normalize domain to lowercase while keeping local part lowercased for standard comparison
    normalized = normalized.lower()

    if not EMAIL_REGEX.match(normalized):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address",
        )

    # Ensure domain has at least one period and valid TLD length >= 2
    domain_part = normalized.split("@", 1)[1]
    if "." not in domain_part or len(domain_part.split(".")[-1]) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address with a valid domain",
        )

    return normalized


def normalize_and_validate_mobile(mobile: str) -> str:
    """
    Validates and normalizes an Indian mobile number.
    - Strips whitespace, dashes, parentheses, dots
    - Accepts formats:
        +919876543210
        +91 9876543210
        919876543210
        09876543210
        9876543210
    - Canonical E.164 storage: +91XXXXXXXXXX
    """
    if not mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number is required",
        )

    # Strip formatting
    cleaned = re.sub(r"[\s\-\(\)\.]", "", mobile.strip())

    # Check and strip leading prefixes
    if cleaned.startswith("+91"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = cleaned[1:]

    if not INDIAN_MOBILE_10_REGEX.match(cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9",
        )

    # Canonical representation: +91XXXXXXXXXX
    return f"+91{cleaned}"
