export interface LeadResponse {
  id: string;
  npi: string;
  name: string;
  phone?: string | null;
  specialty?: string | null;
  state?: string | null;
  created_at: string;
}

export interface LeadListResponse {
  total: number;
  limit: number;
  offset: number;
  data: LeadResponse[];
}

