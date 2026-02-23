"""Basic API key authentication helpers."""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from src.core.config import settings


def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """FastAPI dependency that enforces a static API key header."""
    expected = settings.API_KEY

    if not expected:
        # Misconfiguration: API key not set on the server
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key is not configured on the server",
        )

    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

