"""Lead schemas for request/response validation."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from src.db.models import LeadStatus


class LeadBase(BaseModel):
    """Base lead schema."""
    doctor_id: int
    patient_name: str
    patient_email: Optional[EmailStr] = None
    patient_phone: Optional[str] = None
    condition: str
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a lead."""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    patient_name: Optional[str] = None
    patient_email: Optional[EmailStr] = None
    patient_phone: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[LeadStatus] = None


class LeadResponse(LeadBase):
    """Schema for lead response."""
    id: int
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
