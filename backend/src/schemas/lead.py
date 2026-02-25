"""
FILE PURPOSE:
This file defines Pydantic schemas (data validators) for the Lead model.
Schemas control what data can be sent to and received from the API.

They ensure:
- Only valid data gets accepted from the frontend
- The API always returns data in the expected format
- Required fields are present and optional fields are clearly marked

THINK OF IT AS: The "rules" for what data is allowed in API requests and responses.
"""

# Import tools for data validation and type hints
from datetime import datetime  # For timestamp fields
from typing import List, Optional  # Type hints for lists and optional fields
from uuid import UUID  # Unique identifier type
from pydantic import BaseModel  # Base class for Pydantic models


class LeadBase(BaseModel):
    """
    Base Lead schema - contains the core fields all Lead schemas share.
    
    These are the main fields that describe a doctor:
    - NPI: unique national provider identifier
    - Name: full name of the doctor
    - Phone: contact phone number
    - Specialty: type of medical practice (taxonomy code)
    - State: state where they practice
    """

    # National Provider Identifier (required)
    npi: str
    # Doctor's full name (required)
    name: str
    # Business phone number (optional)
    phone: Optional[str] = None
    # Medical specialty code (optional)
    specialty: Optional[str] = None
    # State code like "TX" or "NY" (optional)
    state: Optional[str] = None


class LeadCreate(LeadBase):
    """
    Schema for creating a new lead.
    Inherits all fields from LeadBase (doesn't add any new ones).
    Used when the frontend sends a request to create a doctor record.
    """
    pass


class LeadUpdate(BaseModel):
    """
    Schema for updating an existing lead.
    
    IMPORTANT: All fields are optional here!
    This allows updating just the fields the frontend provides.
    For example, you could update only the phone number and leave other fields unchanged.
    """

    # All fields are optional for updates
    npi: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None


class LeadResponse(LeadBase):
    """
    Schema for the API response when returning a lead.
    
    This includes all LeadBase fields PLUS two automatic fields:
    - id: unique identifier assigned by the database
    - created_at: timestamp of when the record was created
    """

    # Unique identifier for this lead (assigned by database)
    id: UUID
    # When this doctor record was added to the database
    created_at: datetime

    class Config:
        # from_attributes=True allows converting database models to Pydantic models
        # This is needed because id and created_at come from the database
        from_attributes = True


class LeadListResponse(BaseModel):
    """
    Schema for paginated list responses.
    
    When the frontend requests a list of leads with filters and pagination,
    we return this structure with:
    - total: how many matches exist (for knowing total pages)
    - limit: how many results were requested per page
    - offset: how many results were skipped
    - data: the actual list of leads for this page
    """

    # Total number of leads matching the filters (for pagination math)
    total: int
    # How many results per page (requested limit)
    limit: int
    # How many results were skipped (for offset pagination)
    offset: int
    # The actual list of leads for this page
    data: List[LeadResponse]
