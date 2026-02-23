"""Lead service layer for business logic."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.db.models import Lead
from src.schemas.lead import LeadCreate, LeadUpdate


def get_lead(db: Session, lead_id: UUID) -> Optional[Lead]:
    """Get a lead by ID."""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(db: Session, skip: int = 0, limit: int = 100) -> List[Lead]:
    """Get all leads with pagination."""
    return db.query(Lead).offset(skip).limit(limit).all()


def create_lead(db: Session, lead: LeadCreate) -> Lead:
    """Create a new lead."""
    db_lead = Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def update_lead(db: Session, lead_id: UUID, lead_update: LeadUpdate) -> Optional[Lead]:
    """Update a lead."""
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return None

    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lead, field, value)

    db.commit()
    db.refresh(db_lead)
    return db_lead


def delete_lead(db: Session, lead_id: UUID) -> bool:
    """Delete a lead."""
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return False

    db.delete(db_lead)
    db.commit()
    return True
