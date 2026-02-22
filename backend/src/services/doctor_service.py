"""Doctor service layer for business logic."""
from sqlalchemy.orm import Session
from typing import List, Optional
from src.db.models import Doctor
from src.schemas.doctor import DoctorCreate, DoctorUpdate


def get_doctor(db: Session, doctor_id: int) -> Optional[Doctor]:
    """Get a doctor by ID."""
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def get_doctor_by_email(db: Session, email: str) -> Optional[Doctor]:
    """Get a doctor by email."""
    return db.query(Doctor).filter(Doctor.email == email).first()


def get_doctors(db: Session, skip: int = 0, limit: int = 100) -> List[Doctor]:
    """Get all doctors with pagination."""
    return db.query(Doctor).offset(skip).limit(limit).all()


def create_doctor(db: Session, doctor: DoctorCreate) -> Doctor:
    """Create a new doctor."""
    db_doctor = Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def update_doctor(db: Session, doctor_id: int, doctor_update: DoctorUpdate) -> Optional[Doctor]:
    """Update a doctor."""
    db_doctor = get_doctor(db, doctor_id)
    if not db_doctor:
        return None
    
    update_data = doctor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doctor, field, value)
    
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def delete_doctor(db: Session, doctor_id: int) -> bool:
    """Delete a doctor."""
    db_doctor = get_doctor(db, doctor_id)
    if not db_doctor:
        return False
    
    db.delete(db_doctor)
    db.commit()
    return True
