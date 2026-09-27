import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import EstimatesPage from './EstimatesPage';
import { useEstimateStore } from '@/store/estimateStore';
import { listEstimates, deleteEstimate, duplicateEstimate } from '@/lib/api';
import type { EstimateSummary } from '@/types';

vi.mock('@/components/shared/Navbar', () => ({ default: () => null }));
vi.mock('@/components/shared/Sidebar', () => ({ default: () => null }));
vi.mock('@/components/shared/SEOHead', () => ({ default: () => null }));
vi.mock('@/components/shared/CurrencySelector', () => ({ default: () => null }));
vi.mock('@/components/ThemeProvider', () => ({ useTheme: () => ({ resolvedTheme: 'light' }) }));
vi.mock('@/App', () => ({ useToast: () => ({ addToast: vi.fn() }) }));
vi.mock('@/lib/api', () => ({ listEstimates: vi.fn(), getEstimate: vi.fn(), deleteEstimate: vi.fn(), duplicateEstimate: vi.fn() }));
vi.mock('@/store/currencyStore', () => ({ useCurrencyStore: Object.assign(
  () => ({ format: (value: number) => `$${value}` }),
  { getState: () => ({ refreshRatesIfStale: vi.fn() }) },
) }));

const summary = (id: string): EstimateSummary => ({ id, project_name: `Project ${id}`, project_type: 'Web App',
  cost_likely_usd: 100, cost_min_usd: 80, cost_max_usd: 120, risk_score: 1, risk_level: 'Low',
  confidence_pct: 0, duration_likely_weeks: 4, status: 'completed', version: 1, created_at: '2026-09-27' });
const response = (id: string) => ({ data: { estimates: [summary(id)], total: 21 } }) as Awaited<ReturnType<typeof listEstimates>>;
const mount = () => render(<MemoryRouter><EstimatesPage /></MemoryRouter>);

describe('estimates navigation and recovery', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    useEstimateStore.setState({ estimates: [], totalEstimates: 0, page: 1, perPage: 20, sort: 'created_at_desc',
      filterType: null, loading: false, error: null });
    vi.mocked(listEstimates).mockImplementation(async params => response(String(params?.page || 1)));
  });

  it('reaches later pages with real links and resets pagination when filtering', async () => {
    const user = userEvent.setup();
    mount();
    expect(await screen.findByRole('link', { name: 'Project 1' })).toHaveAttribute('href', '/estimate/1/results');
    expect(screen.getByRole('button', { name: 'Previous page' })).toBeDisabled();
    await user.click(screen.getByRole('button', { name: 'Next page' }));
    expect(await screen.findByRole('link', { name: 'Project 2' })).toHaveAttribute('href', '/estimate/2/results');
    expect(screen.getByRole('button', { name: 'Next page' })).toBeDisabled();
    await user.selectOptions(screen.getByLabelText('Filter by project type'), 'Web App');
    await waitFor(() => expect(listEstimates).toHaveBeenLastCalledWith(expect.objectContaining({ page: 1, project_type: 'Web App' })));
  });

  it('offers retry rather than claiming a failed request is an empty account', async () => {
    vi.mocked(listEstimates).mockRejectedValueOnce(new Error('offline'));
    const user = userEvent.setup();
    mount();
    expect(await screen.findByRole('alert')).toHaveTextContent("couldn't complete");
    await user.click(screen.getByRole('button', { name: 'Retry' }));
    expect(await screen.findByRole('link', { name: 'Project 1' })).toBeVisible();
  });

  it('returns to the previous page after deleting the last item', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(deleteEstimate).mockResolvedValue({ data: {} } as Awaited<ReturnType<typeof deleteEstimate>>);
    const user = userEvent.setup();
    mount();
    await screen.findByRole('link', { name: 'Project 1' });
    await user.click(screen.getByRole('button', { name: 'Next page' }));
    await user.click(await screen.findByRole('button', { name: 'Delete Project 2' }));
    await waitFor(() => expect(useEstimateStore.getState().page).toBe(1));
    expect(deleteEstimate).toHaveBeenCalledWith('2');
  });

  it('provides a labelled duplication action', async () => {
    vi.mocked(duplicateEstimate).mockResolvedValue({ data: {} } as Awaited<ReturnType<typeof duplicateEstimate>>);
    const user = userEvent.setup();
    mount();
    await user.click(await screen.findByRole('button', { name: 'Duplicate Project 1' }));
    expect(duplicateEstimate).toHaveBeenCalledWith('1');
    await waitFor(() => expect(listEstimates).toHaveBeenCalledTimes(2));
  });
});
