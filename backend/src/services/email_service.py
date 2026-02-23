"""Email validation via Abstract API.

This module is responsible only for talking to the external API and
returning the structured result.
"""

from __future__ import annotations

from typing import Any, Dict

import requests

from src.core.config import settings


ABSTRACT_EMAIL_ENDPOINT = "https://emailvalidation.abstractapi.com/v1/"


class EmailValidationError(Exception):
    """Raised when email validation fails for infrastructure reasons."""


def validate_email(email: str) -> Dict[str, Any]:
    """Validate an email address using Abstract's Email Validation API.

    Returns the JSON response from Abstract.
    Raises EmailValidationError if the API key is missing or the request fails.
    """
    api_key = settings.ABSTRACT_EMAIL_API_KEY
    if not api_key:
        raise EmailValidationError("ABSTRACT_EMAIL_API_KEY is not configured")

    try:
        response = requests.get(
            ABSTRACT_EMAIL_ENDPOINT,
            params={"api_key": api_key, "email": email},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise EmailValidationError(f"Error calling Abstract API: {exc}") from exc

    if response.status_code != 200:
        raise EmailValidationError(
            f"Abstract API returned status {response.status_code}: {response.text}"
        )

    return response.json()

