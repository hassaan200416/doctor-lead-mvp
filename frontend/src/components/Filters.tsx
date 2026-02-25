/*
FILE PURPOSE:
This is a React component that displays the filter controls.
Users can search by name, filter by state, filter by specialty, or export results.

WHAT IT DOES:
- Shows 4 input fields: search, state, specialty, and export button
- When user types in a field, it calls a callback function to update the parent
- The parent component (LeadsPage) handles the actual filtering

THINK OF IT AS: The "filter toolbar" at the top of the page.
*/

/**
 * Props (input parameters) for the Filters component.
 * These are passed from the parent (LeadsPage) component.
 */
export interface FiltersProps {
  // Current value of the state filter input (e.g., "TX")
  stateFilter?: string;
  // Current value of the specialty filter input (e.g., "207RP1001X")
  specialtyFilter?: string;
  // Current value of the search input (e.g., "Smith")
  searchTerm?: string;
  // Function to call when user changes the state filter
  onStateChange: (value: string | undefined) => void;
  // Function to call when user changes the specialty filter
  onSpecialtyChange: (value: string | undefined) => void;
  // Function to call when user types in the search field
  onSearchChange: (value: string) => void;
  // Function to call when user clicks the Export button
  onExport: () => void;
}

/**
 * Filters component: Shows filter inputs and export button.
 */
export function Filters({
  stateFilter,
  specialtyFilter,
  searchTerm,
  onStateChange,
  onSpecialtyChange,
  onSearchChange,
  onExport,
}: FiltersProps) {
  return (
    <div>
      {/* Search by doctor name input */}
      <input
        type="text"
        placeholder="Search by name"
        value={searchTerm ?? ""} // Show current search term or empty string
        // When user types, call the search change callback
        onChange={(e) => onSearchChange(e.target.value)}
      />

      {/* Filter by state input (e.g., "TX") */}
      <input
        type="text"
        placeholder="State (e.g. TX)"
        value={stateFilter ?? ""} // Show current state or empty string
        // When user types, call the state change callback
        // If empty, pass undefined instead of empty string
        onChange={(e) => onStateChange(e.target.value || undefined)}
      />

      {/* Filter by specialty code input */}
      <input
        type="text"
        placeholder="Specialty code (e.g. 363LF0000X)"
        value={specialtyFilter ?? ""} // Show current specialty or empty string
        // When user types, call the specialty change callback
        // If empty, pass undefined instead of empty string
        onChange={(e) => onSpecialtyChange(e.target.value || undefined)}
      />

      {/* Export button to download as CSV */}
      <button type="button" onClick={onExport}>
        Export CSV
      </button>
    </div>
  );
}

export default Filters;
