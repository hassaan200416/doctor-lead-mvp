/**
 * TypeScript type definitions
 */

// Doctor types
export interface Doctor {
  id: number;
  name: string;
  specialty: string;
  email: string;
  phone?: string;
  practice_name?: string;
  location?: string;
  created_at: string;
  updated_at: string;
}

export interface DoctorCreate {
  name: string;
  specialty: string;
  email: string;
  phone?: string;
  practice_name?: string;
  location?: string;
}

export interface DoctorUpdate {
  name?: string;
  specialty?: string;
  email?: string;
  phone?: string;
  practice_name?: string;
  location?: string;
}

// Lead types
export const LeadStatus = {
  NEW: 'new',
  CONTACTED: 'contacted',
  QUALIFIED: 'qualified',
  CONVERTED: 'converted',
  LOST: 'lost',
} as const;

export type LeadStatus = (typeof LeadStatus)[keyof typeof LeadStatus];

export interface Lead {
  id: number;
  doctor_id: number;
  patient_name: string;
  patient_email?: string;
  patient_phone?: string;
  condition: string;
  notes?: string;
  status: LeadStatus;
  created_at: string;
  updated_at: string;
}

export interface LeadCreate {
  doctor_id: number;
  patient_name: string;
  patient_email?: string;
  patient_phone?: string;
  condition: string;
  notes?: string;
}

export interface LeadUpdate {
  patient_name?: string;
  patient_email?: string;
  patient_phone?: string;
  condition?: string;
  notes?: string;
  status?: LeadStatus;
}

// API Response types
export interface ApiError {
  detail: string;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}
