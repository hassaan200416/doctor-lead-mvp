"""Lead service layer for business logic and querying."""

from io import StringIO
import csv
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.db.models import Lead
from src.db.session import SessionLocal
from src.schemas.lead import LeadCreate, LeadUpdate


def get_lead(db: Session, lead_id: UUID) -> Optional[Lead]:
    """Get a lead by ID."""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Lead]:
    """Get leads with optional state/specialty filters and pagination.

    This function manages its own database session for simplicity.
    """
    db: Session = SessionLocal()
    try:
        query = db.query(Lead).order_by(Lead.created_at.desc())

        if state:
            query = query.filter(Lead.state == state)

        if specialty:
            query = query.filter(Lead.specialty == specialty)

        return query.offset(offset).limit(limit).all()
    finally:
        db.close()


def get_leads_with_count(
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[int, List[Lead]]:
    """Get leads and total count for given filters and pagination."""
    db: Session = SessionLocal()
    try:
        base_query = db.query(Lead)

        if state:
            base_query = base_query.filter(Lead.state == state)

        if specialty:
            base_query = base_query.filter(Lead.specialty == specialty)

        if search:
            pattern = f"%{search}%"
            base_query = base_query.filter(Lead.name.ilike(pattern))

        total = base_query.count()

        items = (
            base_query.order_by(Lead.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return total, items
    finally:
        db.close()


def get_lead_by_npi(db: Session, npi: str) -> Optional[Lead]:
    """Get a single lead by NPI."""
    return db.query(Lead).filter(Lead.npi == npi).first()


def search_by_specialty(
    db: Session, specialty_code: str, limit: int = 100, offset: int = 0
) -> List[Lead]:
    """Search leads by taxonomy specialty code."""
    return (
        db.query(Lead)
        .filter(Lead.specialty == specialty_code)
        .order_by(Lead.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def search_by_state(
    db: Session, state: str, limit: int = 100, offset: int = 0
) -> List[Lead]:
    """Search leads by state."""
    return (
        db.query(Lead)
        .filter(Lead.state == state)
        .order_by(Lead.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def _search_by_state_and_specialty(
    db: Session, state: str, specialty_code: str, limit: int = 100, offset: int = 0
) -> List[Lead]:
    """Internal helper: search by both state and specialty."""
    return (
        db.query(Lead)
        .filter(Lead.state == state, Lead.specialty == specialty_code)
        .order_by(Lead.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


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


def export_leads_to_csv(
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    search: Optional[str] = None,
) -> str:
    """Export filtered leads to a CSV string."""
    db: Session = SessionLocal()
    try:
        query = db.query(Lead)

        if state:
            query = query.filter(Lead.state == state)

        if specialty:
            query = query.filter(Lead.specialty == specialty)

        if search:
            pattern = f"%{search}%"
            query = query.filter(Lead.name.ilike(pattern))

        leads: List[Lead] = (
            query.order_by(Lead.created_at.desc()).all()
        )

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["id", "npi", "name", "phone", "specialty", "state", "created_at"],
        )
        writer.writeheader()

        for lead in leads:
            writer.writerow(
                {
                    "id": str(lead.id),
                    "npi": lead.npi,
                    "name": lead.name,
                    "phone": lead.phone or "",
                    "specialty": lead.specialty or "",
                    "state": lead.state or "",
                    "created_at": lead.created_at.isoformat() if lead.created_at else "",
                }
            )

        return output.getvalue()
    finally:
        db.close()
