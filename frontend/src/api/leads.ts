import apiClient from './client';
import type { LeadListResponse } from '../types/lead';

export interface GetLeadsParams {
  state?: string;
  specialty?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export async function getLeads(params: GetLeadsParams): Promise<LeadListResponse> {
  const response = await apiClient.get<LeadListResponse>('/leads/', {
    params,
  });
  return response.data;
}

export async function exportLeads(params: Omit<GetLeadsParams, 'limit' | 'offset'>) {
  const response = await apiClient.get<Blob>('/leads/export', {
    params,
    responseType: 'blob',
  });
  return response.data;
}

