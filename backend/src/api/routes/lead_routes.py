"""
FILE PURPOSE:
This file defines all the API endpoints (routes) that the frontend can call to:
- Create, read, update, and delete leads
- Search and filter leads by state, specialty, or doctor name
- Export leads as a CSV file for download
- Validate email addresses for doctors

All routes require a valid API key in the X-API-Key header for security.

THINK OF IT AS: The "menu" of actions the frontend can request from the backend.
"""

# Imports: Tools for building API endpoints
from typing import Any, Dict, Optional  # Type hints for function arguments and returns
from uuid import UUID  # Unique identifier type for leads
import io  # Tool to work with text/file data

from fastapi import APIRouter, Depends, HTTPException, Query, status  # FastAPI tools
from fastapi.responses import StreamingResponse  # For sending file downloads
from sqlalchemy.orm import Session  # Database session for queries

from src.db.database import get_db  # Function to get database connection
from pydantic import BaseModel, EmailStr  # Tools for data validation

from src.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse  # Data structures
from src.services import lead_service  # Business logic for leads
from src.services.email_service import validate_email, EmailValidationError  # Email validation logic
from src.core.security import verify_api_key  # Function to check API key


# Define a request body model for email validation
class EmailValidationRequest(BaseModel):
    """
    This defines what data the frontend must send when validating an email.
    It must include an 'email' field with a valid email address.
    """
    email: EmailStr


# Create the API router: This groups all lead endpoints together
# dependencies=[Depends(verify_api_key)] means ALL these routes require a valid API key
router = APIRouter(
    prefix="/leads",  # All routes start with /leads (becomes /api/v1/leads due to main.py)
    tags=["leads"],  # Tag for organizing documentation
    dependencies=[Depends(verify_api_key)],  # Require API key for every endpoint
)


# --- ENDPOINT 1: Create a new lead ---
@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """
    Create a new doctor lead.
    
    WHAT IT DOES:
    - Takes lead information from the frontend
    - Adds it to the database
    - Returns the new lead with its ID
    
    HTTP Status: 201 (Created) - means the lead was successfully added
    """
    return lead_service.create_lead(db=db, lead=lead)


# --- ENDPOINT 2: Get leads with filtering and pagination ---
@router.get("/", response_model=LeadListResponse)
def read_leads(
    # Optional filter by state (e.g., "TX" for Texas)
    state: Optional[str] = Query(None, description="Filter by 2-letter state code"),
    # Optional filter by medical specialty code (e.g., "207RP1001X")
    specialty: Optional[str] = Query(
        None, description="Filter by taxonomy specialty code (e.g. 207RP1001X)"
    ),
    # Optional search: looks for this text in doctor names (case-insensitive)
    search: Optional[str] = Query(
        None, description="Case-insensitive search on doctor name"
    ),
    # Limit: how many results to show per page (max 1000, default 50)
    limit: int = Query(50, ge=1, le=1000),
    # Offset: how many results to skip (for pagination)
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """
    Get a list of doctor leads with optional filters and pagination.
    
    WHAT IT DOES:
    - Builds a database query with any filters the frontend asked for
    - Calculates total number of matches
    - Returns the requested page of results
    
    EXAMPLE:
    - state="TX" returns only doctors in Texas
    - specialty="207RP1001X" returns only doctors with that medical specialty
    - search="John" returns doctors whose name contains "John"
    - limit=20, offset=40 returns results 40-60 (3rd page with 20 per page)
    """
    # Call the service to get the total count and the filtered results
    total, items = lead_service.get_leads_with_count(
        state=state,
        specialty=specialty,
        search=search,
        limit=limit,
        offset=offset,
    )

    # Return the response in the exact format the frontend expects
    return {
        "total": total,  # Total number of matches (for knowing total pages)
        "limit": limit,  # How many per page
        "offset": offset,  # How many we skipped
        "data": items,  # The actual list of leads for this page
    }


# --- ENDPOINT 3: Export leads as a CSV file (for download) ---
@router.get("/export")
def export_leads(
    # Same optional filters as the list endpoint
    state: Optional[str] = Query(None, description="Filter by 2-letter state code"),
    specialty: Optional[str] = Query(
        None, description="Filter by taxonomy specialty code (e.g. 207RP1001X)"
    ),
    search: Optional[str] = Query(
        None, description="Case-insensitive search on doctor name"
    ),
):
    """
    Export filtered leads as a downloadable CSV file.
    
    WHAT IT DOES:
    - Applies the same filters (state, specialty, search) as the list endpoint
    - Converts ALL matching results to CSV format (no pagination)
    - Sends the file to the frontend with filename "leads.csv"
    
    EXAMPLE:
    - Combine all filters then download as Excel-compatible CSV
    - Frontend automatically saves this as "leads.csv"
    """
    # Get the CSV text from the service
    csv_data = lead_service.export_leads_to_csv(
        state=state,
        specialty=specialty,
        search=search,
    )

    # Send back as a downloadable file
    return StreamingResponse(
        io.StringIO(csv_data),  # Convert text to file-like object
        media_type="text/csv",  # Tell browser this is a CSV file
        headers={
            "Content-Disposition": 'attachment; filename="leads.csv"',  # Filename for download
        },
    )


# --- ENDPOINT 4: Get a single lead by ID ---
@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead(lead_id: UUID, db: Session = Depends(get_db)):
    """
    Get details about one specific doctor lead.
    
    WHAT IT DOES:
    - Takes the lead ID from the URL
    - Looks it up in the database
    - Returns the lead details or "not found" error
    
    EXAMPLE: GET /api/v1/leads/123e4567-e89b-12d3-a456-426614174000
    """
    db_lead = lead_service.get_lead(db, lead_id=lead_id)
    
    # If no lead found, return 404 error
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return db_lead


# --- ENDPOINT 5: Update a lead ---
@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: UUID, lead: LeadUpdate, db: Session = Depends(get_db)):
    """
    Update an existing doctor lead with new information.
    
    WHAT IT DOES:
    - Takes the lead ID and new information
    - Updates those fields in the database
    - Returns the updated lead
    
    NOTE: You can send partial data (doesn't require all fields)
    """
    # Call service to update the lead
    db_lead = lead_service.update_lead(db, lead_id=lead_id, lead_update=lead)
    
    # If no lead found, return 404 error
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return db_lead


# --- ENDPOINT 6: Delete a lead ---
@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a doctor lead from the database.
    
    WHAT IT DOES:
    - Takes the lead ID
    - Removes it from the database
    - Returns empty response (204 means success with no data)
    """
    success = lead_service.delete_lead(db, lead_id=lead_id)
    
    # If no lead found, return 404 error
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return None


# --- ENDPOINT 7: Validate email for a doctor ---
@router.post("/{npi}/validate-email")
def validate_lead_email(
    npi: str,  # National Provider Identifier (unique doctor number)
    payload: EmailValidationRequest,  # The email to validate
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Check if an email address is valid and deliverable.
    
    WHAT IT DOES:
    - Takes a doctor's NPI number and an email address
    - Calls an external email validation service (Abstract API)
    - Returns whether the email can receive messages
    
    NOTE: Currently does NOT save the email to the database.
    The email validation result is only returned to the frontend.
    """
    # Look up the doctor by their NPI number
    lead = lead_service.get_lead_by_npi(db, npi=npi)
    if not lead:
        # Doctor not found in database
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found for provided NPI",
        )

    # Call the email validation service
    try:
        validation = validate_email(payload.email)
    except EmailValidationError as exc:
        # Email service is down or has an error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    # Extract whether the email is deliverable (can receive messages)
    is_deliverable = validation.get("deliverability") == "DELIVERABLE"

    # Return the validation results
    return {
        "npi": npi,
        "email": payload.email,
        "is_deliverable": is_deliverable,  # True if email can receive messages
        "validation": validation,  # Full details from the validation service
        "lead_id": str(lead.id),
    }
