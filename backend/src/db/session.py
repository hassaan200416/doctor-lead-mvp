"""Database session utilities for scripts and background jobs.

This module reuses the main application's engine and Base so that all
models share the same metadata and connection configuration.
"""

from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from src.db.database import Base, engine as engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

