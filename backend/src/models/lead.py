"""Lead ORM model matching the Supabase `leads` table.

This is the canonical Lead model; other modules should import from here.
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from src.db.database import Base


class Lead(Base):
    """Lead model aligned with Supabase `leads` schema."""

    __tablename__ = "leads"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        index=True,
    )

    npi = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    state = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

