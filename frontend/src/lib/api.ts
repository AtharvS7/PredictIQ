import axios from 'axios';
import { supabase } from './supabase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Session Token Cache ──────────────────────────────────
// Avoids expensive async supabase.auth.getSession() on every request
let _cachedToken: string | null = null;

// Listen for auth state changes and update the cached token
supabase.auth.onAuthStateChange((_event, session) => {
  _cachedToken = session?.access_token ?? null;
});

// Bootstrap: seed the cache once on module load
supabase.auth.getSession().then(({ data: { session } }) => {
  _cachedToken = session?.access_token ?? null;
});

// Track if a token refresh is already in progress to prevent stampede
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

// Request interceptor: attach cached JWT (synchronous — no await!)
api.interceptors.request.use((config) => {
  if (_cachedToken) {
    config.headers.Authorization = `Bearer ${_cachedToken}`;
  }
  return config;
});

// Response interceptor: handle 401 with single-retry (no infinite loop)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh once per request — prevent infinite loop
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // If already refreshing, wait for the in-flight refresh
      if (isRefreshing && refreshPromise) {
        const newToken = await refreshPromise;
        if (newToken) {
          _cachedToken = newToken;
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api.request(originalRequest);
        }
        return Promise.reject(error);
      }

      // Start a new refresh
      isRefreshing = true;
      refreshPromise = supabase.auth.refreshSession().then(({ data: { session } }) => {
        isRefreshing = false;
        refreshPromise = null;
        const token = session?.access_token ?? null;
        _cachedToken = token;
        return token;
      }).catch(() => {
        isRefreshing = false;
        refreshPromise = null;
        _cachedToken = null;
        return null;
      });

      const newToken = await refreshPromise;
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api.request(originalRequest);
      }

      // Refresh failed — user is not authenticated, don't retry
      return Promise.reject(error);
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
export const exportPDF = (id: string, currency: string = 'USD') =>
  api.get(`/estimates/${id}/export/pdf`, {
    responseType: 'blob',
    params: { currency },
  });

export const exportJSON = (id: string) =>
  api.get(`/estimates/${id}/export/json`);
