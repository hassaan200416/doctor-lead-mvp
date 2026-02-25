/*
FILE PURPOSE:
This React component displays pagination controls (Previous/Next buttons).
It also shows the current page number and lets users change page size.

WHAT IT DOES:
- Shows "Previous" button (disabled on first page)
- Shows current page number (e.g., "Page 2 of 5")
- Shows "Next" button (disabled on last page)
- Shows an input to change how many results per page

THINK OF IT AS: The "navigation controls" at the bottom of the page.
*/

/**
 * Props (input parameters) for the Pagination component.
 */
export interface PaginationProps {
  // Total number of doctors matching the current filters
  total: number;
  // How many results per page
  limit: number;
  // How many results to skip (0 = first page, 50 = second page if limit=50)
  offset: number;
  // Function to call when user changes the page size (limit)
  onLimitChange: (limit: number) => void;
  // Function to call when user clicks Previous or Next
  onPageChange: (nextOffset: number) => void;
}

/**
 * Pagination component: Shows page navigation controls.
 */
export function Pagination({
  total,
  limit,
  offset,
  onLimitChange,
  onPageChange,
}: PaginationProps) {
  // Ensure limit is valid (at least 1)
  const safeLimit = limit > 0 ? limit : 1;

  // Calculate which page we're on (0-indexed internally, display as 1-indexed)
  // offset=0, limit=50 -> page 0 -> show page 1
  // offset=50, limit=50 -> page 1 -> show page 2
  const currentPage = Math.floor(offset / safeLimit);

  // Calculate total number of pages
  // total=1000, limit=50 -> 1000/50 = 20 pages
  // total=0 -> at least 1 page
  const totalPages = Math.max(1, Math.ceil(total / safeLimit));

  // Can we go to the previous page? (only if offset > 0)
  const canGoPrev = offset > 0;

  // Can we go to the next page? (only if not on last page)
  // offset=50, limit=50, total=1000 -> 50+50 < 1000 -> true
  const canGoNext = offset + safeLimit < total;

  return (
    <div>
      {/* Previous button - disabled if on first page */}
      <button
        type="button"
        disabled={!canGoPrev}
        onClick={() => onPageChange(Math.max(0, offset - safeLimit))}
      >
        Previous
      </button>

      {/* Current page indicator */}
      <span>
        Page {Math.min(currentPage + 1, totalPages)} of {totalPages}
      </span>

      {/* Next button - disabled if on last page */}
      <button
        type="button"
        disabled={!canGoNext}
        onClick={() => onPageChange(offset + safeLimit)}
      >
        Next
      </button>

      {/* Limit (results per page) selector */}
      <span>
        {" "}
        | Limit:{" "}
        <input
          type="number"
          value={safeLimit}
          min={1} // Minimum 1 result per page
          max={1000} // Maximum 1000 results per page
          // When user changes the limit, call the callback
          onChange={(e) => onLimitChange(Number(e.target.value) || 1)}
        />
      </span>
    </div>
  );
}

export default Pagination;
