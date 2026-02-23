"""Database models for the application.

This module re-exports ORM models from the dedicated `models` package.
"""

from src.models.lead import Lead

__all__ = ["Lead"]
