import { useEffect, useState } from 'react';

import { exportLeads, getLeads } from '../api/leads';
import type { LeadResponse, LeadListResponse } from '../types/lead';
import { Filters } from '../components/Filters';
import { LeadsTable } from '../components/LeadsTable';
import { Pagination } from '../components/Pagination';

const DEFAULT_LIMIT = 50;
const SEARCH_DEBOUNCE_MS = 300;

export function LeadsPage() {
  const [leads, setLeads] = useState<LeadResponse[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [limit, setLimit] = useState<number>(DEFAULT_LIMIT);
  const [offset, setOffset] = useState<number>(0);

  const [stateFilter, setStateFilter] = useState<string | undefined>(undefined);
  const [specialtyFilter, setSpecialtyFilter] = useState<string | undefined>(undefined);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Reset pagination when filters/search change
  useEffect(() => {
    setOffset(0);
  }, [stateFilter, specialtyFilter, debouncedSearch]);

  // Debounce search term
  useEffect(() => {
    const handle = window.setTimeout(() => {
      setDebouncedSearch(searchTerm.trim() || '');
    }, SEARCH_DEBOUNCE_MS);

    return () => {
      window.clearTimeout(handle);
    };
  }, [searchTerm]);

  const fetchLeads = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        state: stateFilter || undefined,
        specialty: specialtyFilter || undefined,
        search: debouncedSearch || undefined,
        limit,
        offset,
      };

      const response: LeadListResponse = await getLeads(params);

      setLeads(response.data);
      setTotal(response.total);
    } catch (err) {
      // In a real app we might inspect the error shape
      setError('Failed to load leads. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch whenever filters, pagination, or debounced search change
  useEffect(() => {
    void fetchLeads();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stateFilter, specialtyFilter, debouncedSearch, limit, offset]);

  const handleExport = async () => {
    try {
      const blob = await exportLeads({
        state: stateFilter || undefined,
        specialty: specialtyFilter || undefined,
        search: debouncedSearch || undefined,
      });

      const url = window.URL.createObjectURL(
        new Blob([blob], { type: 'text/csv;charset=utf-8;' }),
      );

      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'leads.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch {
      setError('Failed to export leads. Please try again.');
    }
  };

  return (
    <div>
      <h1>Leads</h1>

      <Filters
        searchTerm={searchTerm}
        stateFilter={stateFilter}
        specialtyFilter={specialtyFilter}
        onSearchChange={setSearchTerm}
        onStateChange={setStateFilter}
        onSpecialtyChange={setSpecialtyFilter}
        onExport={handleExport}
      />

      <div>
        {error && <p>{error}</p>}
        {!error && (
          <div>
            <p>
              Showing {leads.length} of {total} leads
            </p>
            <LeadsTable leads={leads} loading={loading} />
          </div>
        )}
      </div>

      <div>
        <Pagination
          total={total}
          limit={limit}
          offset={offset}
          onLimitChange={(nextLimit) => setLimit(nextLimit || DEFAULT_LIMIT)}
          onPageChange={setOffset}
        />
      </div>
    </div>
  );
}

export default LeadsPage;

