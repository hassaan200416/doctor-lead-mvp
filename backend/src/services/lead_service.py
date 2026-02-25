"""
FILE PURPOSE:
This file contains the business logic for all lead operations.
It's the "thinking part" that handles:
- Finding leads in the database
- Filtering by state, specialty, or name
- Creating, updating, and deleting leads
- Converting leads to CSV format for downloads

This file is separate from the API routes, which makes the code cleaner and testable.
If the database changes, you only update this file, not all the routes.

THINK OF IT AS: The "brain" that decides how to work with doctor lead data.
"""

# Import tools for file handling and database queries
from io import StringIO  # Create in-memory text file for CSV
import csv  # Tools for reading/writing CSV data
from typing import List, Optional  # Type hints
from uuid import UUID  # Unique identifier type

from sqlalchemy.orm import Session  # Database session for queries

from src.db.models import Lead  # The Lead database model
from src.db.session import SessionLocal  # Session factory for background jobs
from src.schemas.lead import LeadCreate, LeadUpdate  # Data validation schemas


# ---------- READ OPERATIONS (Getting data) ----------

def get_lead(db: Session, lead_id: UUID) -> Optional[Lead]:
    """
    Find a single lead by its unique ID.
    
    WHAT IT DOES:
    1. Query the database for a lead with matching ID
    2. Return the lead if found, or None if not found
    
    EXAMPLE: Find the lead with ID "123e4567-e89b-12d3-a456-426614174000"
    """
    # Query: SELECT * FROM leads WHERE id = lead_id LIMIT 1
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_leads(
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Lead]:
    """
    Get a list of leads with optional filters and pagination.
    This function creates its own database session (used for background jobs).
    
    WHAT IT DOES:
    1. Connect to the database
    2. Filter by state and/or specialty if provided
    3. Sort by newest first (created_at DESC)
    4. Skip 'offset' results and take 'limit' results
    5. Return the results
    
    EXAMPLE: Get 50 leads from Texas (skip first 100, so results 100-150)
    """
    db: Session = SessionLocal()  # Create a new database session
    try:
        # Start with the base query: SELECT * FROM leads
        query = db.query(Lead).order_by(Lead.created_at.desc())

        # If state filter provided, only include that state
        # Example: WHERE state = 'TX'
        if state:
            query = query.filter(Lead.state == state)

        # If specialty filter provided, only include that specialty
        # Example: WHERE specialty = '207RP1001X'
        if specialty:
            query = query.filter(Lead.specialty == specialty)

        # Apply pagination: skip 'offset' number and take 'limit' number
        # Example: OFFSET 100 LIMIT 50 (skip 100, take 50)
        return query.offset(offset).limit(limit).all()
    finally:
        # Always close the session when done (cleanup database connection)
        db.close()


def get_leads_with_count(
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[int, List[Lead]]:
    """
    Get leads AND the total count of matches (for pagination).
    This is the main function used by the API list endpoint.
    
    WHAT IT DOES:
    1. Build a query with all filters (state, specialty, name search)
    2. Count total matches (before pagination)
    3. Apply pagination (offset/limit)
    4. Return tuple: (total_count, list_of_leads)
    
    EXAMPLE:
    - Get doctors in Texas with specialty code "207RP1001X" whose name contains "Smith"
    - Return (total=45, leads=[first 20 of those 45])
    """
    db: Session = SessionLocal()  # Create a new database session
    try:
        # Start with base query: SELECT * FROM leads
        base_query = db.query(Lead)

        # Apply state filter if provided
        # Example: WHERE state = 'TX'
        if state:
            base_query = base_query.filter(Lead.state == state)

        # Apply specialty filter if provided
        # Example: WHERE specialty = '207RP1001X'
        if specialty:
            base_query = base_query.filter(Lead.specialty == specialty)

        # Apply name search filter if provided
        # searchis case-insensitive (ILIKE)
        # Example: WHERE name ILIKE '%smith%' (matches "smith", "Smith", "SMITH", etc.)
        if search:
            # Build the search pattern with wildcards: "%search%"
            # This finds "search" anywhere in the doctor's name
            pattern = f"%{search}%"
            base_query = base_query.filter(Lead.name.ilike(pattern))

        # Count total matches BEFORE applying pagination
        # This tells us if there are 45 matches, 100 matches, etc.
        total = base_query.count()

        # Now apply pagination to get just the requested page
        # Sort by newest first, then skip 'offset' and take 'limit'
        items = (
            base_query.order_by(Lead.created_at.desc())  # Newest first
            .offset(offset)  # Skip this many results
            .limit(limit)  # Take this many results
            .all()
        )

        # Return both the total count and the page of results
        return total, items
    finally:
        # Always close the session when done (cleanup database connection)
        db.close()


def get_lead_by_npi(db: Session, npi: str) -> Optional[Lead]:
    """
    Find a single lead by its NPI (National Provider Identifier).
    NPI is unique for each doctor.
    
    WHAT IT DOES:
    1. Query the database for a lead with matching NPI
    2. Return the lead if found, or None if not found
    
    EXAMPLE: Find the lead with NPI "1012345678"
    """
    # Query: SELECT * FROM leads WHERE npi = npi LIMIT 1
    return db.query(Lead).filter(Lead.npi == npi).first()


# ---------- CREATE OPERATIONS (Adding data) ----------

def create_lead(db: Session, lead: LeadCreate) -> Lead:
    """
    Create a new lead (add a new doctor to the database).
    
    WHAT IT DOES:
    1. Take the lead information from the API request
    2. Create a new Lead object in the database
    3. Commit the transaction
    4. Return the new lead (with its newly assigned ID and timestamp)
    
    EXAMPLE: Create a new doctor named "John Smith" in Texas
    """
    # Convert the Pydantic schema to a dictionary and create a Lead database object
    db_lead = Lead(**lead.model_dump())
    
    # Add the lead to the current transaction (doesn't save yet)
    db.add(db_lead)
    
    # Commit the transaction (actually saves to the database)
    db.commit()
    
    # Refresh the lead object to get the auto-generated fields (id, created_at)
    db.refresh(db_lead)
    
    # Return the new lead with all its fields including id and created_at
    return db_lead


# ---------- UPDATE OPERATIONS (Changing data) ----------

def update_lead(db: Session, lead_id: UUID, lead_update: LeadUpdate) -> Optional[Lead]:
    """
    Update an existing lead with new information.
    Only updates fields that were provided (partial updates allowed).
    
    WHAT IT DOES:
    1. Find the lead by ID
    2. Update only the fields that were provided
    3. Save to database
    4. Return the updated lead
    
    EXAMPLE: Update only the phone number for a doctor, leave other fields unchanged
    """
    # Get the existing lead from the database
    db_lead = get_lead(db, lead_id)
    
    # If lead not found, return None
    if not db_lead:
        return None

    # Get only the fields that were provided (exclude fields set to None)
    update_data = lead_update.model_dump(exclude_unset=True)
    
    # Update each field that was provided
    for field, value in update_data.items():
        setattr(db_lead, field, value)  # Set Python attribute = database column

    # Commit the changes to the database
    db.commit()
    
    # Refresh the lead object to ensure we have the latest data
    db.refresh(db_lead)
    
    # Return the updated lead
    return db_lead


# ---------- DELETE OPERATIONS (Removing data) ----------

def delete_lead(db: Session, lead_id: UUID) -> bool:
    """
    Delete a lead from the database.
    
    WHAT IT DOES:
    1. Find the lead by ID
    2. Delete it from the database
    3. Return True if successful, False if lead not found
    
    EXAMPLE: Delete the doctor with a specific ID
    """
    # Get the existing lead from the database
    db_lead = get_lead(db, lead_id)
    
    # If lead not found, return False
    if not db_lead:
        return False

    # Delete the lead from the database
    db.delete(db_lead)
    
    # Commit the deletion to the database
    db.commit()
    
    # Return True to indicate successful deletion
    return True


# ---------- EXPORT OPERATIONS (Getting data in a different format) ----------

def export_leads_to_csv(
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    search: Optional[str] = None,
) -> str:
    """
    Export all filtered leads as a CSV (comma-separated values) string.
    This is used for downloading leads as an Excel-compatible file.
    
    WHAT IT DOES:
    1. Query the database with the same filters as the list endpoint
    2. Convert each lead to a CSV row
    3. Return the entire CSV as a text string
    
    EXAMPLE: Export all doctors in Texas as a CSV file the user can download
    """
    db: Session = SessionLocal()  # Create a new database session
    try:
        # Start with base query: SELECT * FROM leads
        query = db.query(Lead)

        # Apply state filter if provided
        if state:
            query = query.filter(Lead.state == state)

        # Apply specialty filter if provided
        if specialty:
            query = query.filter(Lead.specialty == specialty)

        # Apply name search filter if provided (same as list endpoint)
        if search:
            # Search pattern with wildcards for case-insensitive search
            pattern = f"%{search}%"
            query = query.filter(Lead.name.ilike(pattern))

        # Get all matching leads (no limit/offset for export - get everything)
        leads: List[Lead] = (
            query.order_by(Lead.created_at.desc()).all()  # Newest first
        )

        # Create an in-memory text file for the CSV
        output = StringIO()
        
        # Create a CSV writer that will write to our output
        writer = csv.DictWriter(
            output,
            # Column names for the CSV file
            fieldnames=["id", "npi", "name", "phone", "specialty", "state", "created_at"],
        )
        
        # Write the header row (column names)
        writer.writeheader()

        # Write each lead as a CSV row
        for lead in leads:
            writer.writerow(
                {
                    "id": str(lead.id),  # Convert UUID to string
                    "npi": lead.npi,
                    "name": lead.name,
                    "phone": lead.phone or "",  # Empty string if phone is None
                    "specialty": lead.specialty or "",  # Empty string if specialty is None
                    "state": lead.state or "",  # Empty string if state is None
                    "created_at": lead.created_at.isoformat(),  # Format timestamp as ISO string
                }
            )

        # Get the CSV text and return it
        return output.getvalue()
    finally:
        # Always close the session when done (cleanup database connection)
        db.close()
