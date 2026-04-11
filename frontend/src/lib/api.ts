import axios from 'axios';
import { supabase } from './supabase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

// Response interceptor: handle 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const { data: { session } } = await supabase.auth.refreshSession();
      if (session) {
        error.config.headers.Authorization = `Bearer ${session.access_token}`;
        return api.request(error.config);
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// ── API Functions ────────────────────────────────────────

export const healthCheck = () => api.get('/health');

// Documents
export const confirmDocumentUpload = (data: {
  storage_path: string;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
}) => api.post('/documents/upload', data);

export const getDocument = (id: string) => api.get(`/documents/${id}`);

// Estimates
export const analyzeEstimate = (data: {
  document_id: string;
  overrides?: Record<string, unknown>;
}) => api.post('/estimates/analyze', data);

export const createManualEstimate = (data: {
  project_name: string;
  project_type: string;
  team_size: number;
  duration_months: number;
  complexity: string;
  methodology: string;
  hourly_rate_usd: number;
  tech_stack: string[];
}) => api.post('/estimates/manual', data);

export const listEstimates = (params?: {
  page?: number;
  per_page?: number;
  sort?: string;
  project_type?: string;
}) => api.get('/estimates', { params });

export const getEstimate = (id: string) => api.get(`/estimates/${id}`);

export const duplicateEstimate = (id: string) =>
  api.post(`/estimates/${id}/duplicate`);

export const deleteEstimate = (id: string) =>
  api.delete(`/estimates/${id}`);

export const createShareLink = (id: string, data: {
  expires_in_days?: number;
  password?: string;
}) => api.post(`/estimates/${id}/share`, data);

// Export
export const exportPDF = (id: string) =>
  api.get(`/estimates/${id}/export/pdf`, { responseType: 'blob' });

export const exportJSON = (id: string) =>
  api.get(`/estimates/${id}/export/json`);
