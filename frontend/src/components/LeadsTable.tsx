import type { LeadResponse } from '../types/lead';

export interface LeadsTableProps {
  leads: LeadResponse[];
  loading: boolean;
}

export function LeadsTable({ leads, loading }: LeadsTableProps) {
  if (!loading && leads.length === 0) {
    return <p>No leads match your filters.</p>;
  }

  return (
    <div style={{ position: 'relative' }}>
      {loading && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(0, 0, 0, 0.05)',
            pointerEvents: 'none',
          }}
        >
          <span>Loading leads...</span>
        </div>
      )}
      <table style={loading ? { opacity: 0.5 } : undefined}>
        <thead>
          <tr>
            <th>NPI</th>
            <th>Name</th>
            <th>Phone</th>
            <th>Specialty</th>
            <th>State</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td>{lead.npi}</td>
              <td>{lead.name}</td>
              <td>{lead.phone}</td>
              <td>{lead.specialty}</td>
              <td>{lead.state}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LeadsTable;

