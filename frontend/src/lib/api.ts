import axios from 'axios';
import { auth } from './firebase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Track if a token refresh is already in progress to prevent stampede
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

// Request interceptor: attach Firebase ID token
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401 with single-retry (force token refresh)
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
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api.request(originalRequest);
        }
        return Promise.reject(error);
      }

      // Start a new refresh (force token refresh)
      isRefreshing = true;
      refreshPromise = (async () => {
        try {
          const user = auth.currentUser;
          if (!user) return null;
          // Force refresh the ID token
          const token = await user.getIdToken(true);
          return token;
        } catch {
          return null;
        } finally {
          isRefreshing = false;
          refreshPromise = null;
        }
      })();

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

export const uploadDocumentFile = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/documents/upload-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

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

export const extractDocumentParams = (documentId: string) =>
  api.post(`/documents/${documentId}/extract`);
