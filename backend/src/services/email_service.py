"""
FILE PURPOSE:
This file handles email validation by calling an external service (Abstract API).
It checks if an email address is valid and can receive messages.

IT DOES ONE THING ONLY:
- Takes an email address
- Sends it to Abstract's email validation service
- Returns whether the email is deliverable or not

This is separate from other code so it's easy to replace with a different
email validation service if needed.

THINK OF IT AS: The "email checker" that talks to an external service.
"""

# Import tools for making web requests and type hints
from __future__ import annotations  # Allow forward type hints
from typing import Any, Dict  # Type hints for dictionaries and values

import requests  # Library for making HTTP requests

from src.core.config import settings  # Load API key from configuration


# The web address of Abstract's email validation service
ABSTRACT_EMAIL_ENDPOINT = "https://emailvalidation.abstractapi.com/v1/"


class EmailValidationError(Exception):
    """
    Custom error class for email validation failures.
    
    Raised when:
    - The API key is not configured
    - The API service is down
    - The API returns an error
    
    This lets us distinguish email validation errors from other types of errors.
    """


def validate_email(email: str) -> Dict[str, Any]:
    """
    Check if an email address is valid and deliverable.
    
    WHAT IT DOES:
    1. Gets the Abstract API key from settings
    2. Sends the email to Abstract's service
    3. Gets back information about whether the email is valid
    4. Returns the full response with details
    
    RETURNS: Dictionary with email validation results, example:
    {
        "email": "john@example.com",
        "is_valid_format": true,
        "is_smtp_valid": true,
        "deliverability": "DELIVERABLE",  # This is what we mainly care about
        ...
    }
    
    RAISES: EmailValidationError if:
    - API key not configured
    - Service is down
    - Request fails
    """
    # Get the Abstract API key from our configuration (.env file)
    api_key = settings.ABSTRACT_EMAIL_API_KEY
    
    # Check if the API key is configured
    if not api_key:
        raise EmailValidationError("ABSTRACT_EMAIL_API_KEY is not configured")

    # Try to make the request to Abstract's API
    try:
        # Send HTTP GET request to the Abstract email validation service
        response = requests.get(
            ABSTRACT_EMAIL_ENDPOINT,
            # Parameters to send:
            # - api_key: Our authentication key
            # - email: The email address to validate
            params={"api_key": api_key, "email": email},
            # timeout: Give up after 10 seconds if no response
            timeout=10,
        )
    except requests.RequestException as exc:
        # If the request fails (network error, timeout, etc.)
        raise EmailValidationError(f"Error calling Abstract API: {exc}") from exc

    # Check if the response was successful (HTTP 200 = OK)
    if response.status_code != 200:
        # If not 200, the API returned an error
        raise EmailValidationError(
            f"Abstract API returned status {response.status_code}: {response.text}"
        )

    # Convert the JSON response to a Python dictionary and return it
    return response.json()

