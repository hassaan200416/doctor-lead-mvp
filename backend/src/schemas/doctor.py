"""Doctor schemas for request/response validation."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class DoctorBase(BaseModel):
    """Base doctor schema."""
    name: str
    specialty: str
    email: EmailStr
    phone: Optional[str] = None
    practice_name: Optional[str] = None
    location: Optional[str] = None


class DoctorCreate(DoctorBase):
    """Schema for creating a doctor."""
    pass


class DoctorUpdate(BaseModel):
    """Schema for updating a doctor."""
    name: Optional[str] = None
    specialty: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    practice_name: Optional[str] = None
    location: Optional[str] = None


class DoctorResponse(DoctorBase):
    """Schema for doctor response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
