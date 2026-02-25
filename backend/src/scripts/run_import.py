"""
FILE PURPOSE:
This is a command-line script that:
1. Loads and processes the NPPES doctor data from the CSV file
2. Shows you a preview (first 5 records)
3. Inserts the processed doctors into the database
4. Tells you how many doctors were added (skipping duplicates)

WHY THIS FILE EXISTS:
This script is useful for importing doctors from the CSV file without using the web API.
It's used for one-time data loads or testing the import pipeline.

HOW TO RUN:
Open a terminal in the backend folder and type:
    python -m src.scripts.run_import

THINK OF IT AS: The "one-click importer" for loading doctor data from CSV.
"""

# Import language features and path tools
from __future__ import annotations  # Allow forward type hints
from pathlib import Path  # Tool for working with file paths
from pprint import pprint  # Pretty print tool for showing data nicely

# Import the CSV processing functions
from src.services.npi_loader import load_npi_data, insert_leads


# Build the path to the CSV file
# This goes up 2 folder levels from this script to find the 'data' folder
# src/scripts/run_import.py -> src/scripts -> src -> backend -> data/npi_raw.csv
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "npi_raw.csv"


def main() -> None:
    """
    Main function that runs the import process.
    
    WHAT IT DOES (step by step):
    1. Load and process doctors from the CSV file
    2. Show how many doctors were processed
    3. Display the first 5 doctors as a preview
    4. Insert all doctors into the database
    5. Report how many were actually added (duplicates skipped)
    """
    # Step 1: Load and clean the CSV data
    # This returns a list of doctor dictionaries ready to save
    leads = load_npi_data(DATA_PATH)

    # Count how many doctors we processed
    total = len(leads)
    print(f"Total filtered records: {total}")

    # Show a preview of the first 5 doctors (or fewer if less than 5)
    preview_count = min(5, total)
    print(f"\nFirst {preview_count} records:")
    for record in leads[:preview_count]:
        # pprint displays the data nicely formatted
        pprint(record)

    # Step 2: Insert all the processed doctors into the database
    print(f"\nInserting {total} leads (duplicates will be skipped)...")
    # This function returns how many were actually inserted (excluding duplicates)
    inserted = insert_leads(leads)
    # Report the results
    print(f"Inserted {inserted} new leads")


# This code runs when the script is executed directly (not imported as a module)
if __name__ == "__main__":
    main()

