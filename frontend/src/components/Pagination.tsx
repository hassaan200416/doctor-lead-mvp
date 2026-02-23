export interface PaginationProps {
  total: number;
  limit: number;
  offset: number;
  onLimitChange: (limit: number) => void;
  onPageChange: (nextOffset: number) => void;
}

export function Pagination({ total, limit, offset, onLimitChange, onPageChange }: PaginationProps) {
  const safeLimit = limit > 0 ? limit : 1;
  const currentPage = Math.floor(offset / safeLimit);
  const totalPages = Math.max(1, Math.ceil(total / safeLimit));

  const canGoPrev = offset > 0;
  const canGoNext = offset + safeLimit < total;

  return (
    <div>
      <button type="button" disabled={!canGoPrev} onClick={() => onPageChange(Math.max(0, offset - safeLimit))}>
        Previous
      </button>

      <span>
        Page {Math.min(currentPage + 1, totalPages)} of {totalPages}
      </span>

      <button type="button" disabled={!canGoNext} onClick={() => onPageChange(offset + safeLimit)}>
        Next
      </button>

      <span>
        {' '}
        | Limit:{' '}
        <input
          type="number"
          value={safeLimit}
          min={1}
          max={1000}
          onChange={(e) => onLimitChange(Number(e.target.value) || 1)}
        />
      </span>
    </div>
  );
}

export default Pagination;

