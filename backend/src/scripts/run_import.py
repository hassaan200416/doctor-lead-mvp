"""CLI script to test the NPI CSV filtering engine.

Run from the backend directory:

    python -m src.scripts.run_import
"""

from __future__ import annotations

from pathlib import Path
from pprint import pprint

from src.services.npi_loader import load_npi_data, insert_leads


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "npi_raw.csv"


def main() -> None:
    leads = load_npi_data(DATA_PATH)

    total = len(leads)
    print(f"Total filtered records: {total}")

    preview_count = min(5, total)
    print(f"\nFirst {preview_count} records:")
    for record in leads[:preview_count]:
        pprint(record)

    print(f"\nInserting {total} leads (duplicates will be skipped)...")
    inserted = insert_leads(leads)
    print(f"Inserted {inserted} new leads")


if __name__ == "__main__":
    main()

