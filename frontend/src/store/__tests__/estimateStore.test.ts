import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useEstimateStore } from '../estimateStore';
import { deleteEstimate, getEstimate } from '@/lib/api';
import type { EstimateResult, EstimateSummary } from '@/types';

vi.mock('@/lib/api', () => ({
  listEstimates: vi.fn(), getEstimate: vi.fn(), deleteEstimate: vi.fn(),
}));

describe('estimate request failures', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    useEstimateStore.setState({ estimates: [], totalEstimates: 0, currentEstimate: null, error: null, loading: false });
  });

  it('clears stale results and finishes loading after a failed fetch', async () => {
    useEstimateStore.setState({ currentEstimate: { estimate_id: 'old' } as EstimateResult });
    vi.mocked(getEstimate).mockRejectedValue(new Error('Estimate not found'));
    await useEstimateStore.getState().fetchEstimate('missing');
    expect(useEstimateStore.getState()).toMatchObject({ currentEstimate: null, loading: false, error: 'Estimate not found' });
  });

  it('rejects deletion failures and preserves the estimate and count', async () => {
    const estimate = { id: 'saved' } as EstimateSummary;
    useEstimateStore.setState({ estimates: [estimate], totalEstimates: 1 });
    vi.mocked(deleteEstimate).mockRejectedValue(new Error('Deletion failed'));
    await expect(useEstimateStore.getState().removeEstimate('saved')).rejects.toThrow('Deletion failed');
    expect(useEstimateStore.getState()).toMatchObject({ estimates: [estimate], totalEstimates: 1, error: 'Deletion failed' });
  });

  it('removes successful deletions and clears a cached result', async () => {
    useEstimateStore.setState({ estimates: [{ id: 'saved' } as EstimateSummary], totalEstimates: 1, currentEstimate: { estimate_id: 'saved' } as EstimateResult });
    vi.mocked(deleteEstimate).mockResolvedValue({ data: {} } as Awaited<ReturnType<typeof deleteEstimate>>);
    await useEstimateStore.getState().removeEstimate('saved');
    expect(useEstimateStore.getState()).toMatchObject({ estimates: [], totalEstimates: 0, currentEstimate: null, error: null });
  });
});
