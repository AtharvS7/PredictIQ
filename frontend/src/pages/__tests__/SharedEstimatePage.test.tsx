import { afterEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import SharedEstimatePage from '../SharedEstimatePage';

const result = {
  project_name: 'Shared CRM', version: 1, created_at: '2026-01-01',
  inputs: { project_type: 'Web App', team_size: 4, duration_months: 6, complexity: 'Medium', tech_stack: ['React'] },
  outputs: { cost_likely_usd: 10000, cost_min_usd: 8000, cost_max_usd: 14000, effort_likely_hours: 200,
    timeline_likely_weeks: 24, risk_level: 'Low', confidence_pct: 70, top_risks: [] },
};
function mount() {
  render(<MemoryRouter initialEntries={['/share/token']}><Routes>
    <Route path="/share/:token" element={<SharedEstimatePage />} />
  </Routes></MemoryRouter>);
}
afterEach(() => vi.unstubAllGlobals());

describe('public shared estimate', () => {
  it('renders without login or private owner fields', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => result }));
    mount();
    expect(await screen.findByRole('heading', { name: 'Shared CRM' })).toBeInTheDocument();
    expect(screen.getByText(/Read only/)).toBeInTheDocument();
    expect(screen.getByText(/not calibrated probabilities/)).toBeInTheDocument();
  });
  it('renders an expired link as an error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));
    mount();
    expect(await screen.findByRole('alert')).toHaveTextContent(/expired or is unavailable/);
  });
  it('posts a password in the body and then displays the estimate', async () => {
    const fetcher = vi.fn().mockResolvedValueOnce({ ok: false, status: 401 })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => result });
    vi.stubGlobal('fetch', fetcher);
    mount();
    fireEvent.change(await screen.findByLabelText('Share password'), { target: { value: 'secret' } });
    fireEvent.click(screen.getByRole('button', { name: 'Open estimate' }));
    expect(await screen.findByRole('heading', { name: 'Shared CRM' })).toBeInTheDocument();
    expect(fetcher.mock.calls[1][1]).toMatchObject({ method: 'POST', body: JSON.stringify({ password: 'secret' }) });
    expect(fetcher.mock.calls[1][0]).not.toContain('secret');
  });
});
