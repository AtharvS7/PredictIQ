import { create } from 'zustand';
import type { EstimateResult, EstimateSummary } from '@/types';
import { listEstimates, getEstimate, deleteEstimate } from '@/lib/api';

interface EstimateState {
  estimates: EstimateSummary[];
  currentEstimate: EstimateResult | null;
  totalEstimates: number;
  loading: boolean;
  error: string | null;
  page: number;
  perPage: number;
  sort: string;
  filterType: string | null;
  fetchEstimates: () => Promise<void>;
  fetchEstimate: (id: string) => Promise<void>;
  removeEstimate: (id: string) => Promise<void>;
  setCurrentEstimate: (estimate: EstimateResult | null) => void;
  setPage: (page: number) => void;
  setSort: (sort: string) => void;
  setFilterType: (type: string | null) => void;
  clearError: () => void;
}

export const useEstimateStore = create<EstimateState>((set, get) => ({
  estimates: [],
  currentEstimate: null,
  totalEstimates: 0,
  loading: false,
  error: null,
  page: 1,
  perPage: 20,
  sort: 'created_at_desc',
  filterType: null,

  fetchEstimates: async () => {
    set({ loading: true, error: null });
    try {
      const { page, perPage, sort, filterType } = get();
      const response = await listEstimates({
        page,
        per_page: perPage,
        sort,
        project_type: filterType || undefined,
      });
      set({
        estimates: response.data.estimates || [],
        totalEstimates: response.data.total || 0,
      });
    } catch (error: unknown) {
      // Don't show error for 401 — user is just not authenticated yet
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosErr = error as { response?: { status?: number } };
        if (axiosErr.response?.status === 401) {
          set({ estimates: [], totalEstimates: 0 });
          return;
        }
      }
      const message = error instanceof Error ? error.message : 'Failed to fetch estimates';
      set({ error: message });
    } finally {
      set({ loading: false });
    }
  },

  fetchEstimate: async (id) => {
    set({ loading: true, error: null });
    try {
      const response = await getEstimate(id);
      set({ currentEstimate: response.data });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to fetch estimate';
      set({ error: message });
    } finally {
      set({ loading: false });
    }
  },

  removeEstimate: async (id) => {
    try {
      await deleteEstimate(id);
      set((state) => ({
        estimates: state.estimates.filter((e) => e.id !== id),
        totalEstimates: state.totalEstimates - 1,
      }));
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to delete estimate';
      set({ error: message });
    }
  },

  setCurrentEstimate: (estimate) => set({ currentEstimate: estimate }),
  setPage: (page) => set({ page }),
  setSort: (sort) => set({ sort }),
  setFilterType: (type) => set({ filterType: type }),
  clearError: () => set({ error: null }),
}));
