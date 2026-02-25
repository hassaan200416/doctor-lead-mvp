"""
FILE PURPOSE:
This file handles loading and processing the NPPES (National Plan & Provider Enumeration System) CSV file.
It takes raw healthcare provider data and:
1. Loads it from the CSV file
2. Filters for only the doctors we want (individual practitioners in Texas for this MVP)
3. Cleans the data (removes duplicates, fixes formatting, removes empty fields)
4. Converts it to the format our database expects
5. Another function saves the cleaned data to the database

THINK OF IT AS: The "data cleaning factory" that transforms messy CSV data into clean records.
"""

# Import tools for file handling and data processing
from __future__ import annotations  # Allow forward type hints
from pathlib import Path  # Tool for working with file paths
from typing import Any, Dict, List, cast  # Type hints

import pandas as pd  # Library for reading and processing CSV files
from sqlalchemy.orm import Session  # Database session for saving data

from src.db.session import SessionLocal  # Session factory for background jobs
from src.models.lead import Lead  # The Lead database model


# ========== PUBLIC FUNCTIONS (Others can call these) ==========

def load_npi_data(csv_path: Path, *, debug: bool = False) -> List[Dict[str, Any]]:
    """
    Main function: Load and process the NPPES CSV file.
    
    WHAT IT DOES:
    1. Load the raw CSV file
    2. Filter for doctors matching our criteria
    3. Clean the data (remove duplicates, fix formatting)
    4. Return a list of cleaned doctor records ready for database insertion
    
    PROCESSING STEPS (in order):
    - Load raw CSV data
    - Filter: Keep only individual doctors (Entity Type Code = "1")
    - Filter: Keep only those with primary taxonomy designation (Y)
    - Filter: Keep only those from Texas (for MVP, currently hardcoded)
    - Clean: Remove duplicates, fix whitespace, remove empty fields
    - Format: Convert to our database column names
    
    RETURNS: List of dictionaries like:
    [{"npi": "1234567890", "name": "Dr. Smith", "phone": "555-1234", "specialty": "207RP1001X", "state": "TX"}, ...]
    """
    # Step 1: Read the CSV file into memory
    df = _load_csv(csv_path, debug=debug)
    
    # Step 2: Filter for only the providers we want
    df = _filter_doctors(df)
    
    # Step 3: Clean up the data
    df = _clean_rows(df)
    
    # Step 4: Reshape into our desired format
    return _format_output(df)


# ========== COLUMN NAME CONSTANTS ==========
# These are the exact column names from the NPPES CSV file
# We store them as constants to avoid typos

# Tells us if this record is an individual (1) or organization (2)
_COL_ENTITY_TYPE = "Entity Type Code"
# Tells us if this is their primary taxonomy/specialty (Y/N)
_COL_PRIMARY_TAXONOMY_SWITCH_1 = "Healthcare Provider Primary Taxonomy Switch_1"
# The state where they practice
_COL_STATE = "Provider Business Practice Location Address State Name"
# National Provider Identifier (unique ID for each provider)
_COL_NPI = "NPI"
# First name of the provider
_COL_FIRST_NAME = "Provider First Name"
# Last name of the provider
_COL_LAST_NAME = "Provider Last Name (Legal Name)"
# Phone number of their business practice
_COL_PHONE = "Provider Business Practice Location Address Telephone Number"
# Medical specialty code (taxonomy)
_COL_TAXONOMY_CODE_1 = "Healthcare Provider Taxonomy Code_1"


# ========== INTERNAL HELPER FUNCTIONS (Starting with _) ==========

def _load_csv(csv_path: Path, *, debug: bool) -> pd.DataFrame:
    """
    Load the NPPES CSV file into a Pandas DataFrame.
    
    WHAT IT DOES:
    1. Check if the file exists
    2. Read the CSV file
    3. Keep everything as text (strings) to preserve NPI leading zeros
    4. Print debug info if requested
    
    RETURNS: A Pandas DataFrame with all rows and columns from the CSV
    """
    # Check if the CSV file exists at the given path
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    # Read the CSV file
    # dtype="string" keeps everything as text (prevents converting "0123" to 123)
    # keep_default_na=False prevents treating "NA" as missing value
    # low_memory=False scans entire file before deciding data types
    df = pd.read_csv(csv_path, dtype="string", keep_default_na=False, low_memory=False)

    # Print debug information if requested
    if debug:
        print(df.columns)  # Show all column names
        print("Total rows in CSV:", len(df))  # Show how many doctors in the file
        # Show sample values from entity type column to understand the data
        if _COL_ENTITY_TYPE in df.columns:
            print(df[_COL_ENTITY_TYPE].unique()[:10])
        else:
            print(f"Column '{_COL_ENTITY_TYPE}' not found.")

    return df


def _filter_doctors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the dataset to keep only doctors matching our MVP criteria.
    
    MVP FILTERS (for this version):
    1. Entity Type Code = "1" means individual provider (not a company)
    2. Primary Taxonomy Switch = "Y" means this is their main specialty
    3. State = "TX" (Texas) for this MVP version
    
    WHAT IT DOES:
    Keeps only rows where ALL three conditions are true.
    Rows that don't match are deleted from the DataFrame.
    """
    # Make sure the required columns exist in the CSV
    _require_columns(df, [_COL_ENTITY_TYPE, _COL_PRIMARY_TAXONOMY_SWITCH_1, _COL_STATE])

    # FILTER 1: Keep only individual doctors (not organizations)
    # "1" = individual, "2" = organization
    df = df[df[_COL_ENTITY_TYPE] == "1"]
    
    # FILTER 2: Keep only those with primary taxonomy designation
    # "Y" means this is their main specialty, "N" means secondary
    df = df[df[_COL_PRIMARY_TAXONOMY_SWITCH_1] == "Y"]

    # FILTER 3: Keep only Texas providers (MVP is hardcoded for TX)
    # In the future, this could be configurable
    df = df[df[_COL_STATE] == "TX"]

    return df


def _clean_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare the data by:
    1. Removing whitespace from fields
    2. Deleting records with missing NPI or phone
    3. Removing duplicate providers (by NPI)
    
    WHAT IT DOES:
    Fixes formatting issues and removes bad/incomplete data.
    """
    # Make sure the required columns exist
    _require_columns(df, [_COL_NPI, _COL_PHONE])

    # Remove leading/trailing whitespace from all fields we'll use
    # This fixes " John Smith " -> "John Smith"
    for col in [
        _COL_NPI,
        _COL_FIRST_NAME,
        _COL_LAST_NAME,
        _COL_PHONE,
        _COL_STATE,
        _COL_TAXONOMY_CODE_1,
    ]:
        # Only clean if the column exists
        if col in df.columns:
            # Convert to text and remove whitespace from both ends
            df[col] = df[col].astype("string").str.strip()

    # Remove records with missing or empty NPI
    # We need NPI as a unique identifier for doctors
    df = df[df[_COL_NPI].notna() & (df[_COL_NPI] != "")]
    
    # Remove records with missing or empty phone
    # Phone is required for our lead records
    df = df[df[_COL_PHONE].notna() & (df[_COL_PHONE] != "")]

    # Ensure NPI is stored as text (already is, but be explicit)
    df[_COL_NPI] = df[_COL_NPI].astype("string")

    # Remove duplicate providers (keep only the first occurrence)
    # Some providers might appear multiple times in the CSV file
    df = df.drop_duplicates(subset=[_COL_NPI], keep="first")

    return df


def _format_output(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert the cleaned DataFrame into our desired output format.
    
    WHAT IT DOES:
    1. Combine first and last names into full name
    2. Rename columns to match our database schema (npi, name, phone, specialty, state)
    3. Convert to list of dictionaries (one per doctor)
    
    RETURNS: List of dictionaries ready to insert into the database
    EXAMPLE: [{"npi": "1234567890", "name": "John Smith", ...}, ...]
    """
    # Make sure all required columns exist
    _require_columns(
        df,
        [_COL_NPI, _COL_FIRST_NAME, _COL_LAST_NAME, _COL_PHONE, _COL_STATE, _COL_TAXONOMY_CODE_1],
    )

    # Combine first and last names into full name
    # If first name is missing, use empty string
    first = df[_COL_FIRST_NAME].fillna("").astype("string").str.strip()
    last = df[_COL_LAST_NAME].fillna("").astype("string").str.strip()
    # Combine with space in between and remove extra whitespace
    name = (first + " " + last).str.strip()

    # Create a new DataFrame with our desired column names
    out = pd.DataFrame(
        {
            "npi": df[_COL_NPI].astype("string").str.strip(),
            "name": name,
            "phone": df[_COL_PHONE].astype("string").str.strip(),
            "specialty": df[_COL_TAXONOMY_CODE_1].astype("string").str.strip(),
            "state": df[_COL_STATE].astype("string").str.strip(),
        }
    )

    # Convert DataFrame to list of dictionaries and return
    return cast(List[Dict[str, Any]], out.to_dict(orient="records"))


def _require_columns(df: pd.DataFrame, required: List[str]) -> None:
    """
    Check that all required columns exist in the DataFrame.
    Raise an error if any are missing.
    
    WHAT IT DOES:
    Validates the CSV structure before processing.
    If expected columns are missing, it means the CSV format has changed.
    """
    # Find which required columns are missing
    missing = [c for c in required if c not in df.columns]
    
    # If any are missing, raise an error with the list of missing columns
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def insert_leads(leads: List[Dict[str, Any]], *, chunk_size: int = 250) -> int:
    """
    Insert cleaned doctor records into the database, one batch at a time.
    Automatically prevents duplicate doctors (by NPI) from being inserted twice.
    
    WHAT IT DOES:
    1. Collects all unique NPI numbers we're about to add
    2. Queries the database once to see which NPIs already exist
    3. Only inserts NEW doctors (not already in database)
    4. Groups them into chunks to avoid memory issues with large datasets
    5. Returns how many new doctors were actually inserted
    
    WHY IN CHUNKS:
    If you have 1 million doctors and try to insert all at once,
    you might run out of memory. So we insert in groups (chunk_size = 250)
    
    RETURNS: Number of newly inserted doctors
    """
    # If no leads to insert, return immediately
    if not leads:
        return 0

    # Extract and clean all unique NPI numbers from the leads
    # This removes duplicates within the current batch
    all_npis = {
        str(lead.get("npi", "")).strip()
        for lead in leads
        if str(lead.get("npi", "")).strip()
    }
    
    # If no valid NPIs, return immediately
    if not all_npis:
        return 0

    # Create a new database session for this insertion
    session: Session = SessionLocal()

    try:
        # QUERY ONCE: Get all NPIs that already exist in the database
        # This is efficient - one database round-trip instead of checking each doctor individually
        existing_npis = {
            row[0]
            for row in session.query(Lead.npi)
            .filter(Lead.npi.in_(list(all_npis)))
            .all()
        }

        # Keep track of how many doctors we actually inserted
        inserted_total = 0
        
        # Start with an empty batch
        batch: List[Lead] = []

        # Process each doctor from the leads list
        for data in leads:
            # Extract and clean the NPI
            npi = str(data.get("npi", "")).strip()
            
            # Skip this doctor if:
            # - No valid NPI
            # - NPI already exists in database
            if not npi or npi in existing_npis:
                continue

            # Mark this NPI as existing (so we don't try to insert it again in this batch)
            existing_npis.add(npi)

            # Create a new Lead database object with the doctor's information
            batch.append(
                Lead(
                    npi=npi,
                    name=str(data.get("name", "")).strip(),
                    phone=str(data.get("phone", "")).strip() or None,  # None if empty
                    specialty=str(data.get("specialty", "")).strip() or None,  # None if empty
                    state=str(data.get("state", "")).strip() or None,  # None if empty
                )
            )

            # When batch reaches the chunk size, insert and commit
            if len(batch) >= chunk_size:
                session.add_all(batch)  # Add all doctors in batch to the session
                session.commit()  # Save to database
                inserted_total += len(batch)  # Count how many we inserted
                batch.clear()  # Empty the batch for next chunk

        # Insert any remaining doctors in the final batch
        if batch:
            session.add_all(batch)  # Add remaining doctors to the session
            session.commit()  # Save to database
            inserted_total += len(batch)  # Count how many we inserted

        # Return the total number of doctors we inserted
        return inserted_total
    except Exception:
        # If something goes wrong, undo all changes (rollback)
        session.rollback()
        # Re-raise the error so it can be handled elsewhere
        raise
    finally:
        # Always close the database connection when done (cleanup)
        session.close()
