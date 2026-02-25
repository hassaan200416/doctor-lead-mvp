/*
FILE PURPOSE:
This file defines TypeScript interfaces (type definitions) for the data structures
used in API requests and responses.

These interfaces help TypeScript catch errors and provide autocomplete.
If the backend returns different data, TypeScript will warn us.

THINK OF IT AS: The "contract" between frontend and backend - what data looks like.
*/

/**
 * LeadResponse: One doctor record.
 * 
 * Fields:
 * - id: Unique identifier for this doctor (UUID)
 * - npi: National Provider Identifier (unique across all US healthcare providers)
 * - name: Full name of the doctor
 * - phone: Business phone number (optional)
 * - specialty: Medical specialty code (optional)
 * - state: State code where they practice (optional)
 * - created_at: When this record was added to the database (ISO timestamp)
 */
export interface LeadResponse {
  // Unique identifier (assigned by database)
  id: string;
  // National Provider Identifier
  npi: string;
  // Doctor's full name
  name: string;
  // Business phone number (? means optional, | null means could be null)
  phone?: string | null;
  // Medical specialty code
  specialty?: string | null;
  // State code (e.g., "TX")
  state?: string | null;
  // When the record was created
  created_at: string;
}

/**
 * LeadListResponse: Response when fetching a list of doctors.
 * 
 * This is what the backend returns when you call the /leads/ endpoint.
 * It includes:
 * - Total number of matching doctors (for pagination math)
 * - Current page size and offset
 * - The list of doctors for this page
 */
export interface LeadListResponse {
  // Total number of doctors matching the filters (for calculating total pages)
  total: number;
  // How many results per page (requested limit)
  limit: number;
  // How many results were skipped (for calculating current page)
  offset: number;
  // The actual list of doctors for this page
  data: LeadResponse[];
}

