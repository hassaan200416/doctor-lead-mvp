"""
FILE PURPOSE:
This file defines the Lead database model (also called an ORM model).
The Lead model represents a single doctor record in the PostgreSQL database.

It maps to the 'leads' table in Supabase with columns for:
- Unique ID for each doctor
- NPI (National Provider Identifier)
- Name, phone number, medical specialty
- State they practice in
- Timestamp of when the record was created

THINK OF IT AS: The "blueprint" for how doctor records are stored in the database.
"""

# Import language features and database tools
from __future__ import annotations  # Allow type hints referencing types defined later
from sqlalchemy import Column, DateTime, String  # Column types
from sqlalchemy.dialects.postgresql import UUID  # UUID type for PostgreSQL
from sqlalchemy.sql import func, text  # SQL functions and raw SQL

from src.db.database import Base  # Base class for all models


class Lead(Base):
    """
    Lead ORM Model - Represents a doctor record in the database.
    
    This class maps to the 'leads' table in PostgreSQL.
    Each instance represents one doctor.
    """

    # Name of the table in the database
    __tablename__ = "leads"

    # UNIQUE ID COLUMN
    # Every doctor gets a unique UUID (universal unique identifier)
    id = Column(
        UUID(as_uuid=True),  # Store as UUID format
        primary_key=True,  # This is the unique identifier (primary key)
        # Automatically generate a new random UUID for each new doctor
        server_default=text("gen_random_uuid()"),
        # Index this column for fast lookups by ID
        index=True,
    )

    # NATIONAL PROVIDER IDENTIFIER COLUMN
    # A unique number assigned to each healthcare provider
    npi = Column(
        String,  # Store as text
        nullable=False,  # This field is required (can't be empty)
        # Index this column for fast lookups by NPI
        index=True,
    )

    # DOCTOR'S NAME COLUMN
    # Full name of the healthcare provider
    name = Column(
        String,  # Store as text
        nullable=False,  # This field is required (can't be empty)
    )

    # PHONE NUMBER COLUMN
    # Business practice phone number
    phone = Column(
        String,  # Store as text
        nullable=True,  # This field is optional (can be empty/null)
    )

    # MEDICAL SPECIALTY COLUMN
    # Taxonomy code representing the doctor's specialty (e.g., "207RP1001X")
    specialty = Column(
        String,  # Store as text
        nullable=True,  # This field is optional (can be empty/null)
    )

    # STATE COLUMN
    # 2-letter state code where the doctor practices (e.g., "TX" for Texas)
    state = Column(
        String,  # Store as text
        nullable=True,  # This field is optional (can be empty/null)
    )

    # CREATION TIMESTAMP COLUMN
    # Records when this doctor's information was added to the database
    created_at = Column(
        DateTime(timezone=True),  # Store date and time with timezone
        # Automatically set to current time when a new doctor is added
        server_default=func.now(),
        nullable=False,  # This field is required (always has a timestamp)
    )

