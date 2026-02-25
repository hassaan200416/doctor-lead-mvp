"""
FILE PURPOSE:
This file provides database session access for background jobs and CLI scripts.
It's a companion to database.py, but for code that runs outside of FastAPI requests.

USES:
- CLI scripts (like importing leads from CSV)
- Background tasks
- Other jobs that don't go through the API

THINK OF IT AS: Database sessions for "offline" operations (not through the web API).
"""

# Import language features and session tools
from __future__ import annotations  # Allow type hints referencing types defined later
from sqlalchemy.orm import sessionmaker  # Creates database sessions

# Import the engine and Base from the main database module
# This ensures all code uses the same database connection and model definitions
from src.db.database import Base, engine as engine


# Create a session factory for background jobs
# This is the same as "SessionLocal" in database.py, but kept here for scripts
SessionLocal = sessionmaker(
    # Don't automatically commit - wait for explicit commit()
    autocommit=False,
    # Don't automatically flush - wait for explicit flush()
    autoflush=False,
    # Connect to the same database engine
    bind=engine
)

