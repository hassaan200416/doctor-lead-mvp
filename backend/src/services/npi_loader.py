"""CSV-based NPI loading, filtering and cleaning.

This module is responsible for:
    - Loading raw NPI CSV data
    - Filtering rows for MVP
    - Cleaning and structuring the result

It does **not** talk to the database.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.models.lead import Lead


# --- Public API -----------------------------------------------------------

def load_npi_data(csv_path: Path, *, debug: bool = False) -> List[Dict[str, Any]]:
    """Load CSV → Filter → Clean → Return structured data."""
    df = _load_csv(csv_path, debug=debug)
    df = _filter_doctors(df)
    df = _clean_rows(df)
    return _format_output(df)


# --- Internal helpers -----------------------------------------------------

_COL_ENTITY_TYPE = "Entity Type Code"
_COL_PRIMARY_TAXONOMY_SWITCH_1 = "Healthcare Provider Primary Taxonomy Switch_1"
_COL_STATE = "Provider Business Practice Location Address State Name"
_COL_NPI = "NPI"
_COL_FIRST_NAME = "Provider First Name"
_COL_LAST_NAME = "Provider Last Name (Legal Name)"
_COL_PHONE = "Provider Business Practice Location Address Telephone Number"
_COL_TAXONOMY_CODE_1 = "Healthcare Provider Taxonomy Code_1"


def _load_csv(csv_path: Path, *, debug: bool) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    # Read everything as strings to avoid losing leading zeros, etc.
    df = pd.read_csv(csv_path, dtype="string", keep_default_na=False, low_memory=False)

    if debug:
        print(df.columns)
        print("Total rows in CSV:", len(df))
        if _COL_ENTITY_TYPE in df.columns:
            print(df[_COL_ENTITY_TYPE].unique()[:10])
        else:
            print(f"Column '{_COL_ENTITY_TYPE}' not found.")

    return df


def _filter_doctors(df: pd.DataFrame) -> pd.DataFrame:
    """Apply MVP filters (no specialty text filter yet)."""
    _require_columns(df, [_COL_ENTITY_TYPE, _COL_PRIMARY_TAXONOMY_SWITCH_1, _COL_STATE])

    df = df[df[_COL_ENTITY_TYPE] == "1"]
    df = df[df[_COL_PRIMARY_TAXONOMY_SWITCH_1] == "Y"]

    # Hardcoded for MVP; not dynamic yet.
    df = df[df[_COL_STATE] == "TX"]

    return df


def _clean_rows(df: pd.DataFrame) -> pd.DataFrame:
    _require_columns(df, [_COL_NPI, _COL_PHONE])

    # Trim whitespace for fields we will use downstream.
    for col in [
        _COL_NPI,
        _COL_FIRST_NAME,
        _COL_LAST_NAME,
        _COL_PHONE,
        _COL_STATE,
        _COL_TAXONOMY_CODE_1,
    ]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    # Drop null/empty NPI and phone
    df = df[df[_COL_NPI].notna() & (df[_COL_NPI] != "")]
    df = df[df[_COL_PHONE].notna() & (df[_COL_PHONE] != "")]

    # Convert NPI to string (already string dtype; keep explicit)
    df[_COL_NPI] = df[_COL_NPI].astype("string")

    # Remove duplicates by NPI
    df = df.drop_duplicates(subset=[_COL_NPI], keep="first")

    return df


def _format_output(df: pd.DataFrame) -> List[Dict[str, str]]:
    _require_columns(
        df,
        [_COL_NPI, _COL_FIRST_NAME, _COL_LAST_NAME, _COL_PHONE, _COL_STATE, _COL_TAXONOMY_CODE_1],
    )

    first = df[_COL_FIRST_NAME].fillna("").astype("string").str.strip()
    last = df[_COL_LAST_NAME].fillna("").astype("string").str.strip()
    name = (first + " " + last).str.strip()

    out = pd.DataFrame(
        {
            "npi": df[_COL_NPI].astype("string").str.strip(),
            "name": name,
            "phone": df[_COL_PHONE].astype("string").str.strip(),
            "specialty": df[_COL_TAXONOMY_CODE_1].astype("string").str.strip(),
            "state": df[_COL_STATE].astype("string").str.strip(),
        }
    )

    return out.to_dict(orient="records")


def _require_columns(df: pd.DataFrame, required: List[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def insert_leads(leads: List[Dict[str, Any]], *, chunk_size: int = 250) -> int:
    """Insert leads into the database, avoiding duplicates by NPI.

    Performs a single query to fetch existing NPIs, then inserts only new ones.
    Returns the number of newly inserted rows.
    """
    if not leads:
        return 0

    # Normalise all NPIs up front
    all_npis = {
        str(lead.get("npi", "")).strip()
        for lead in leads
        if str(lead.get("npi", "")).strip()
    }
    if not all_npis:
        return 0

    session: Session = SessionLocal()

    try:
        # Fetch existing NPIs in a single round-trip
        existing_npis = {
            row[0]
            for row in session.query(Lead.npi)
            .filter(Lead.npi.in_(list(all_npis)))
            .all()
        }

        inserted_total = 0
        batch: List[Lead] = []

        for data in leads:
            npi = str(data.get("npi", "")).strip()
            if not npi or npi in existing_npis:
                continue

            existing_npis.add(npi)

            batch.append(
                Lead(
                    npi=npi,
                    name=str(data.get("name", "")).strip(),
                    phone=str(data.get("phone", "")).strip() or None,
                    specialty=str(data.get("specialty", "")).strip() or None,
                    state=str(data.get("state", "")).strip() or None,
                )
            )

            if len(batch) >= chunk_size:
                session.add_all(batch)
                session.commit()
                inserted_total += len(batch)
                batch.clear()

        if batch:
            session.add_all(batch)
            session.commit()
            inserted_total += len(batch)

        return inserted_total
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

