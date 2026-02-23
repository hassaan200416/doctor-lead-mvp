"""API routes for lead endpoints."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from src.services import lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead."""
    return lead_service.create_lead(db=db, lead=lead)


@router.get("/", response_model=List[LeadResponse])
def read_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all leads with pagination."""
    leads = lead_service.get_leads(db, skip=skip, limit=limit)
    return leads


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
