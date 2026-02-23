"""Lead schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class LeadBase(BaseModel):
    """Base lead schema matching the Supabase `leads` table."""

    npi: str
    name: str
    phone: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a lead."""

    pass


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""

    npi: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema for lead response."""

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Paginated list of leads."""

    total: int
    limit: int
    offset: int
    data: List[LeadResponse]
