import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ResultsPage from '../ResultsPage';
import EstimatesPage from '../EstimatesPage';
import { useEstimateStore } from '@/store/estimateStore';
import { getEstimate, deleteEstimate, listEstimates } from '@/lib/api';
import type { EstimateResult, EstimateSummary } from '@/types';

const { addToast } = vi.hoisted(() => ({ addToast: vi.fn() }));
vi.mock('@/App', () => ({ useToast: () => ({ addToast }) }));
vi.mock('@/components/shared/Navbar', () => ({ default: () => null }));
vi.mock('@/components/shared/Sidebar', () => ({ default: () => null }));
vi.mock('@/components/shared/CurrencySelector', () => ({ default: () => null }));
vi.mock('react-chartjs-2', () => ({ Bar: () => null, PolarArea: () => null, Pie: () => null, Line: () => null }));
vi.mock('@/store/currencyStore', () => {
  const state = { format: (value: number) => `$${value}`, convert: (value: number) => value, symbol: () => '$', refreshRatesIfStale: vi.fn() };
  return { useCurrencyStore: Object.assign(() => state, { getState: () => state }) };
});
vi.mock('@/lib/api', () => ({
  getEstimate: vi.fn(), listEstimates: vi.fn(), deleteEstimate: vi.fn(),
  exportPDF: vi.fn(), duplicateEstimate: vi.fn(), createShareLink: vi.fn(),
}));

function result(risk: 'Low' | 'Medium' | 'High' | 'Critical'): EstimateResult {
  return {
    estimate_id: 'saved', document_id: null, user_id: 'user', project_name: 'Saved project',
    created_at: '2026-01-01', version: 1, status: 'complete', model_version: '1',
    inputs: { project_type: 'Web App', tech_stack: [], team_size: 2, duration_months: 2, complexity: 'Medium', methodology: 'Agile', hourly_rate_usd: 50 },
    outputs: {
      effort_min_hours: 80, effort_likely_hours: 100, effort_max_hours: 120,
      cost_min_usd: 4000, cost_likely_usd: 5000, cost_max_usd: 6000,
      timeline_min_weeks: 1, timeline_likely_weeks: 2, timeline_max_weeks: 3,
      confidence_pct: 80, risk_score: 42, risk_level: risk, top_risks: [], phase_breakdown: [],
      model_explanation: 'Explanation', benchmark_comparison: 'Benchmark',
    },
  };
}

function renderResult() {
  render(<MemoryRouter initialEntries={['/estimate/saved/results']}><Routes>
    <Route path="/estimate/:id/results" element={<ResultsPage />} />
  </Routes></MemoryRouter>);
}

describe('estimate pages', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    useEstimateStore.setState({ estimates: [], currentEstimate: null, totalEstimates: 0, loading: false, error: null });
  });

  it('shows fetch errors and recovers when retry succeeds', async () => {
    vi.mocked(getEstimate).mockRejectedValueOnce(new Error('Estimate not found'))
      .mockResolvedValueOnce({ data: result('Low') } as Awaited<ReturnType<typeof getEstimate>>);
    renderResult();
    expect(await screen.findByRole('alert')).toHaveTextContent('Estimate not found');
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(await screen.findByRole('heading', { name: 'Saved project' })).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it.each([
    ['Low', '#10B981'], ['Medium', '#F59E0B'], ['High', '#EF4444'], ['Critical', '#B91C1C'],
  ] as const)('renders %s risk with the appropriate semantic color', async (level, color) => {
    vi.mocked(getEstimate).mockResolvedValue({ data: result(level) } as Awaited<ReturnType<typeof getEstimate>>);
    renderResult();
    expect(await screen.findByText('42/100')).toHaveStyle({ color });
  });

  it('shows persisted calculation inputs including zero integrations', async () => {
    const estimate = result('Low');
    Object.assign(estimate.inputs, { feature_count: 17, integration_count: 0, volatility_score: 5, team_experience: 3.5, size_fp: 123.45 });
    vi.mocked(getEstimate).mockResolvedValue({ data: estimate } as Awaited<ReturnType<typeof getEstimate>>);
    renderResult();
    await screen.findByRole('heading', { name: 'Saved project' });
    for (const [label, value] of [['Features', '17'], ['Integrations', '0'], ['Requirements Volatility (1–5)', '5'], ['Team Experience (1–4)', '3.5'], ['Function Points', '123.45']]) {
      expect(screen.getByText(label).parentElement).toHaveTextContent(value);
    }
    expect(screen.queryByText('Not recorded')).not.toBeInTheDocument();
  });

  it('does not invent missing calculation inputs on historical estimates', async () => {
    vi.mocked(getEstimate).mockResolvedValue({ data: result('Low') } as Awaited<ReturnType<typeof getEstimate>>);
    renderResult();
    expect(await screen.findAllByText('Not recorded')).toHaveLength(5);
  });

  it('keeps a failed deletion visible and only announces failure', async () => {
    const estimate = { id: 'saved', project_name: 'Saved project', project_type: 'Web App', created_at: '2026-01-01', version: 1, risk_level: 'Low' } as EstimateSummary;
    vi.mocked(listEstimates).mockResolvedValue({ data: { estimates: [estimate], total: 1 } } as Awaited<ReturnType<typeof listEstimates>>);
    vi.mocked(deleteEstimate).mockRejectedValue(new Error('Server unavailable'));
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    render(<MemoryRouter><EstimatesPage /></MemoryRouter>);
    fireEvent.click(await screen.findByTitle('Delete'));
    await waitFor(() => expect(addToast).toHaveBeenCalledWith('error', 'Failed to delete estimate. Please try again.'));
    expect(addToast).not.toHaveBeenCalledWith('info', 'Estimate deleted');
    expect(screen.getByText('Saved project')).toBeInTheDocument();
  });
});
