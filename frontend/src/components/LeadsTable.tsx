/*
FILE PURPOSE:
This React component displays a table of doctors (leads).
It shows a loading overlay while data is being fetched.
It shows an empty state message if there are no results.

WHAT IT DOES:
- Displays all doctors in a table format
- Shows a loading spinner/message while fetching data
- Shows "No leads match your filters" if the list is empty

THINK OF IT AS: The "data table" that shows the list of doctors.
*/

// Import the LeadResponse type definition
import type { LeadResponse } from "../types/lead";

/**
 * Props (input parameters) for the LeadsTable component.
 */
export interface LeadsTableProps {
  // Array of doctors to display in the table
  leads: LeadResponse[];
  // Whether data is currently being loaded from the backend
  loading: boolean;
}

/**
 * LeadsTable component: Displays a table of doctors.
 */
export function LeadsTable({ leads, loading }: LeadsTableProps) {
  // If not loading AND no results, show empty state message
  if (!loading && leads.length === 0) {
    return <p>No leads match your filters.</p>;
  }

  return (
    // Container div with relative positioning (for the loading overlay)
    <div style={{ position: "relative" }}>
      {/* Loading overlay: shown when loading is true */}
      {loading && (
        <div
          style={{
            position: "absolute", // Position over the table
            inset: 0, // Cover the entire parent
            display: "flex", // Center the content
            alignItems: "center", // Vertically centered
            justifyContent: "center", // Horizontally centered
            backgroundColor: "rgba(0, 0, 0, 0.05)", // Slight dark overlay
            pointerEvents: "none", // Don't block clicks to table behind
          }}
        >
          <span>Loading leads...</span>
        </div>
      )}

      {/* The actual table - slightly dimmed while loading */}
      <table style={loading ? { opacity: 0.5 } : undefined}>
        {/* Table header row */}
        <thead>
          <tr>
            <th>NPI</th>
            <th>Name</th>
            <th>Phone</th>
            <th>Specialty</th>
            <th>State</th>
          </tr>
        </thead>
        {/* Table body - one row per doctor */}
        <tbody>
          {/* Map through leads and create a row for each doctor */}
          {leads.map((lead) => (
            <tr key={lead.id}>
              {" "}
              {/* key is required by React for list rendering */}
              <td>{lead.npi}</td> {/* Display NPI */}
              <td>{lead.name}</td> {/* Display name */}
              <td>{lead.phone}</td> {/* Display phone */}
              <td>{lead.specialty}</td> {/* Display specialty code */}
              <td>{lead.state}</td> {/* Display state */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LeadsTable;
