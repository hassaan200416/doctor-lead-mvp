/*
FILE PURPOSE:
This file contains functions that wrap the backend API calls for leads.
It simplifies making requests to the backend by hiding the details of HTTP requests.

WHAT IT DOES:
- getLeads(): Fetch a list of doctors with filters and pagination
- exportLeads(): Download filtered doctors as a CSV file

THINK OF IT AS: The "API wrapper" - a user-friendly interface to talk to the backend.
*/

// Import the HTTP client we configured in client.ts
import apiClient from './client';
// Import the type definition for API responses
import type { LeadListResponse } from '../types/lead';

/**
 * Parameters that can be sent when fetching leads.
 * All parameters are optional - you can filter by any combination of these.
 */
export interface GetLeadsParams {
  state?: string;  // Filter by state code (e.g., "TX")
  specialty?: string;  // Filter by specialty code (e.g., "207RP1001X")
  search?: string;  // Search by doctor name (case-insensitive)
  limit?: number;  // How many results per page (default 50)
  offset?: number;  // How many results to skip (for pagination)
}

/**
 * Fetch a list of doctors (leads) with optional filters and pagination.
 * 
 * WHAT IT DOES:
 * 1. Takes filter/pagination parameters
 * 2. Sends a GET request to the backend /leads/ endpoint
 * 3. Returns the response with the list of doctors and total count
 * 
 * EXAMPLE:
 * const result = await getLeads({ state: 'TX', limit: 20, offset: 0 })
 * // result.total = 1000 (total doctors in TX)
 * // result.data = [first 20 doctors]
 */
export async function getLeads(params: GetLeadsParams): Promise<LeadListResponse> {
  // Make the GET request to /leads/ with the provided parameters
  const response = await apiClient.get<LeadListResponse>('/leads/', {
    params,  // These become query parameters in the URL
  });
  // Return just the data part (not headers, status, etc.)
  return response.data;
}

/**
 * Export filtered doctors as a CSV file for download.
 * 
 * WHAT IT DOES:
 * 1. Takes filter parameters (no pagination for export - get all matching)
 * 2. Sends a GET request to the backend /leads/export endpoint
 * 3. Gets back the CSV file as a binary blob
 * 4. Returns the blob so the page can trigger a download
 * 
 * EXAMPLE:
 * const csvBlob = await exportLeads({ state: 'TX', search: 'Smith' })
 * // Now trigger a download of leads.csv
 */
export async function exportLeads(params: Omit<GetLeadsParams, 'limit' | 'offset'>) {
  // Note: Omit means we remove 'limit' and 'offset' from the parameters
  // (no pagination for export - get all matching results)
  
  // Make the GET request to /leads/export with filters
  const response = await apiClient.get<Blob>('/leads/export', {
    params,  // These become query parameters in the URL
    // responseType: 'blob' tells Axios to return the response as binary data (file)
    responseType: 'blob',
  });
  // Return the CSV file data as a blob
  return response.data;
}

