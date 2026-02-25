/*
FILE PURPOSE:
This is the main page component that orchestrates the entire leads UI.
It manages all the state (filters, pagination, data, loading) and coordinates
the Filters, LeadsTable, and Pagination child components.

WHAT IT DOES:
- Manages filter state (search, state, specialty)
- Handles pagination (limit, offset, calculating pages)
- Fetches leads from the backend API when filters/page changes
- Implements search debouncing (waits 300ms after user stops typing)
- Handles CSV export
- Resets pagination when filters change

THINK OF IT AS: The "orchestrator" that manages the entire leads page.
*/

// Import React hooks
import { useEffect, useState } from "react";

// Import API functions to fetch leads and export to CSV
import { exportLeads, getLeads } from "../api/leads";
// Import type definitions
import type { LeadResponse, LeadListResponse } from "../types/lead";
// Import child components
import { Filters } from "../components/Filters";
import { LeadsTable } from "../components/LeadsTable";
import { Pagination } from "../components/Pagination";

// Constants
const DEFAULT_LIMIT = 50; // Default results per page
const SEARCH_DEBOUNCE_MS = 300; // Wait 300ms after user stops typing before searching

/**
 * LeadsPage component: Main page showing leads table with filters and pagination.
 */
export function LeadsPage() {
  // ========== STATE FOR DATA ==========
  // The list of doctors to display in the table
  const [leads, setLeads] = useState<LeadResponse[]>([]);
  // Total number of doctors matching current filters (for pagination)
  const [total, setTotal] = useState<number>(0);

  // ========== STATE FOR PAGINATION ==========
  // How many results per page
  const [limit, setLimit] = useState<number>(DEFAULT_LIMIT);
  // How many results to skip (offset=0 is first page)
  const [offset, setOffset] = useState<number>(0);

  // ========== STATE FOR FILTERS ==========
  // Current state filter (e.g., "TX")
  const [stateFilter, setStateFilter] = useState<string | undefined>(undefined);
  // Current specialty filter (e.g., "207RP1001X")
  const [specialtyFilter, setSpecialtyFilter] = useState<string | undefined>(
    undefined,
  );
  // What user is currently typing in the search box (immediate, not debounced)
  const [searchTerm, setSearchTerm] = useState<string>("");
  // The debounced search term (used for actual API calls)
  const [debouncedSearch, setDebouncedSearch] = useState<string>("");

  // ========== STATE FOR UI ==========
  // Whether data is currently being loaded from the backend
  const [loading, setLoading] = useState<boolean>(false);
  // Error message to display (if any)
  const [error, setError] = useState<string | null>(null);

  // ========== EFFECT: Reset pagination when filters change ==========
  // When user changes a filter, go back to page 1
  useEffect(() => {
    setOffset(0);
  }, [stateFilter, specialtyFilter, debouncedSearch]);

  // ========== EFFECT: Debounce the search term ==========
  // This prevents sending a request to the backend every keystroke
  useEffect(() => {
    // Set up a timer to update the debounced search after 300ms
    const handle = window.setTimeout(() => {
      setDebouncedSearch(searchTerm.trim() || "");
    }, SEARCH_DEBOUNCE_MS);

    // Cleanup function: clear the timer if user types again before 300ms
    return () => {
      window.clearTimeout(handle);
    };
  }, [searchTerm]);

  // ========== FUNCTION: Fetch leads from backend ==========
  /**
   * Fetches doctors from the backend with current filters and pagination.
   */
  const fetchLeads = async () => {
    // Show loading indicator
    setLoading(true);
    // Clear any previous error
    setError(null);

    try {
      // Build the request parameters
      const params = {
        state: stateFilter || undefined, // Only include if set
        specialty: specialtyFilter || undefined, // Only include if set
        search: debouncedSearch || undefined, // Only include if set
        limit, // Results per page
        offset, // How many to skip
      };

      // Call the API to get leads
      const response: LeadListResponse = await getLeads(params);

      // Update state with the response
      setLeads(response.data); // List of doctors for this page
      setTotal(response.total); // Total available doctors
    } catch (err) {
      // If something goes wrong, show error message
      setError("Failed to load leads. Please try again.");
    } finally {
      // Always hide loading indicator when done (success or error)
      setLoading(false);
    }
  };

  // ========== EFFECT: Fetch leads when filters/pagination change ==========
  // This runs whenever any of the dependencies change
  useEffect(() => {
    // Call fetchLeads but don't wait for it (async)
    void fetchLeads();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stateFilter, specialtyFilter, debouncedSearch, limit, offset]);

  // ========== FUNCTION: Handle CSV export ==========
  /**
   * Export filtered leads as a CSV file for download.
   */
  const handleExport = async () => {
    try {
      // Call the export function with current filters (no pagination for export)
      const blob = await exportLeads({
        state: stateFilter || undefined,
        specialty: specialtyFilter || undefined,
        search: debouncedSearch || undefined,
      });

      // Create a blob with proper CSV type
      const url = window.URL.createObjectURL(
        new Blob([blob], { type: "text/csv;charset=utf-8;" }),
      );

      // Create a temporary download link
      const link = document.createElement("a");
      link.href = url;
      // Set the filename for the download
      link.setAttribute("download", "leads.csv");

      // Add link to page and click it to trigger download
      document.body.appendChild(link);
      link.click();

      // Clean up: remove the link and release the object URL
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch {
      // If export fails, show error message
      setError("Failed to export leads. Please try again.");
    }
  };

  // ========== RENDER ==========
  return (
    <div>
      {/* Page title */}
      <h1>Leads</h1>

      {/* Filter controls component */}
      <Filters
        searchTerm={searchTerm}
        stateFilter={stateFilter}
        specialtyFilter={specialtyFilter}
        // Pass callbacks to update parent state
        onSearchChange={setSearchTerm}
        onStateChange={setStateFilter}
        onSpecialtyChange={setSpecialtyFilter}
        onExport={handleExport}
      />

      {/* Results section */}
      <div>
        {/* Show error if one exists */}
        {error && <p>{error}</p>}
        {/* If no error, show the leads */}
        {!error && (
          <div>
            {/* Show how many leads are displayed */}
            <p>
              Showing {leads.length} of {total} leads
            </p>
            {/* Display the leads in a table */}
            <LeadsTable leads={leads} loading={loading} />
          </div>
        )}
      </div>

      {/* Pagination controls component */}
      <div>
        <Pagination
          total={total}
          limit={limit}
          offset={offset}
          // Pass callbacks to update pagination
          onLimitChange={(nextLimit) => setLimit(nextLimit || DEFAULT_LIMIT)}
          onPageChange={setOffset}
        />
      </div>
    </div>
  );
}

export default LeadsPage;
