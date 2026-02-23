export interface FiltersProps {
  stateFilter?: string;
  specialtyFilter?: string;
  searchTerm?: string;
  onStateChange: (value: string | undefined) => void;
  onSpecialtyChange: (value: string | undefined) => void;
  onSearchChange: (value: string) => void;
  onExport: () => void;
}

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
      <input
        type="text"
        placeholder="Search by name"
        value={searchTerm ?? ''}
        onChange={(e) => onSearchChange(e.target.value)}
      />

      <input
        type="text"
        placeholder="State (e.g. TX)"
        value={stateFilter ?? ''}
        onChange={(e) => onStateChange(e.target.value || undefined)}
      />

      <input
        type="text"
        placeholder="Specialty code (e.g. 363LF0000X)"
        value={specialtyFilter ?? ''}
        onChange={(e) => onSpecialtyChange(e.target.value || undefined)}
      />

      <button type="button" onClick={onExport}>
        Export CSV
      </button>
    </div>
  );
}

export default Filters;

