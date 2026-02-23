"""API routes for lead endpoints."""

from typing import List, Optional
from uuid import UUID
import io

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.db.database import get_db
from pydantic import BaseModel, EmailStr

from src.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse
from src.services import lead_service
from src.services.email_service import validate_email, EmailValidationError
from src.core.security import verify_api_key

router = APIRouter(
    prefix="/leads",
    tags=["leads"],
    dependencies=[Depends(verify_api_key)],
)


class EmailValidationRequest(BaseModel):
    email: EmailStr


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead."""
    return lead_service.create_lead(db=db, lead=lead)


@router.get("/", response_model=LeadListResponse)
def read_leads(
    state: Optional[str] = Query(None, description="Filter by 2-letter state code"),
    specialty: Optional[str] = Query(
        None, description="Filter by taxonomy specialty code (e.g. 207RP1001X)"
    ),
    search: Optional[str] = Query(
        None, description="Case-insensitive search on doctor name"
    ),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get leads with optional state/specialty/name filters and pagination."""
    total, items = lead_service.get_leads_with_count(
        state=state,
        specialty=specialty,
        search=search,
        limit=limit,
        offset=offset,
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": items,
    }


@router.get("/export")
def export_leads(
    state: Optional[str] = Query(None, description="Filter by 2-letter state code"),
    specialty: Optional[str] = Query(
        None, description="Filter by taxonomy specialty code (e.g. 207RP1001X)"
    ),
    search: Optional[str] = Query(
        None, description="Case-insensitive search on doctor name"
    ),
):
    """Export filtered leads as a CSV file."""
    csv_data = lead_service.export_leads_to_csv(
        state=state,
        specialty=specialty,
        search=search,
    )

    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="leads.csv"',
        },
    )


@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead(lead_id: UUID, db: Session = Depends(get_db)):
    """Get a specific lead by ID."""
    db_lead = lead_service.get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return db_lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: UUID, lead: LeadUpdate, db: Session = Depends(get_db)):
    """Update a lead."""
    db_lead = lead_service.update_lead(db, lead_id=lead_id, lead_update=lead)
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return db_lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: UUID, db: Session = Depends(get_db)):
    """Delete a lead."""
    success = lead_service.delete_lead(db, lead_id=lead_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return None


@router.post("/{npi}/validate-email")
def validate_lead_email(
    npi: str,
    payload: EmailValidationRequest,
    db: Session = Depends(get_db),
):
    """Validate an email address for a given NPI.

    Note: Temporarily does NOT persist email to the database because the
    `email` column is not present in the `leads` table.
    """
    lead = lead_service.get_lead_by_npi(db, npi=npi)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found for provided NPI",
        )

    try:
        validation = validate_email(payload.email)
    except EmailValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    is_deliverable = validation.get("deliverability") == "DELIVERABLE"

    return {
        "npi": npi,
        "email": payload.email,
        "is_deliverable": is_deliverable,
        "validation": validation,
        "lead_id": str(lead.id),
    }
