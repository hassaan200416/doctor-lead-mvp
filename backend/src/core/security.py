"""
FILE PURPOSE:
This file contains the security check that protects the API.
All lead endpoints are protected by requiring a valid API key in the request header.

The API key acts like a password:
- Frontend must include it in the "X-API-Key" header of every request
- Backend checks that it matches the secret key from .env
- If the key is missing or wrong, the request is rejected with a 401 error

THINK OF IT AS: The "bouncer at the door" that checks if requests are allowed in.
"""

# Import security tools
from __future__ import annotations  # Allow type hints referencing types defined later
from fastapi import Header, HTTPException, status  # FastAPI tools for headers and errors
from src.core.config import settings  # Load the API key from configuration


def verify_api_key(
    # This parameter reads the "X-API-Key" header from the request
    # If the header is missing, this variable will be None
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
) -> None:
    """
    Validate that the request includes the correct API key.
    
    This function is used as a FastAPI "dependency" on all lead routes.
    If the API key is invalid, this raises an error and blocks the request.
    
    HOW IT WORKS:
    1. Frontend includes the API key in the request header: X-API-Key: secret123
    2. FastAPI extracts this and passes it to this function
    3. We compare it to the secret key from settings (loaded from .env)
    4. If they don't match, we return a 401 error
    5. If they match, the request continues to the actual endpoint
    """
    
    # Get the expected API key from the configuration (from .env file)
    expected = settings.API_KEY

    # CHECK 1: Is the API key configured on the server?
    if not expected:
        # This is a server configuration problem, not a user error
        # Return 500 (Internal Server Error) - the server is misconfigured
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key is not configured on the server",
        )

    # CHECK 2: Does the provided key match the expected key?
    if x_api_key != expected:
        # The key is missing or doesn't match the secret key
        # Return 401 (Unauthorized) - the user is not authenticated
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

