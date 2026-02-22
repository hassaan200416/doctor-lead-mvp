"""API routes for lead endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.database import get_db
from src.db.models import LeadStatus
from src.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from src.services import lead_service, doctor_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead."""
    # Verify doctor exists
    doctor = doctor_service.get_doctor(db, doctor_id=lead.doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return lead_service.create_lead(db=db, lead=lead)


@router.get("/", response_model=List[LeadResponse])
def read_leads(
    skip: int = 0,
    limit: int = 100,
    doctor_id: Optional[int] = Query(None),
    status: Optional[LeadStatus] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all leads with optional filters."""
    if doctor_id is not None:
        leads = lead_service.get_leads_by_doctor(db, doctor_id=doctor_id, skip=skip, limit=limit)
    elif status is not None:
        leads = lead_service.get_leads_by_status(db, status=status, skip=skip, limit=limit)
    else:
        leads = lead_service.get_leads(db, skip=skip, limit=limit)
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific lead by ID."""
    db_lead = lead_service.get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    return db_lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, lead: LeadUpdate, db: Session = Depends(get_db)):
    """Update a lead."""
    db_lead = lead_service.update_lead(db, lead_id=lead_id, lead_update=lead)
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    return db_lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete a lead."""
    success = lead_service.delete_lead(db, lead_id=lead_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    return None
