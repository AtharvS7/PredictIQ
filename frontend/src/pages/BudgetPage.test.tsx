import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import BudgetPage from './BudgetPage';
import { listBudgets, saveBudget, type SavedBudget } from '@/lib/budgets';

vi.mock('@/components/shared/Navbar', () => ({ default: () => null }));
vi.mock('@/components/shared/Sidebar', () => ({ default: () => null }));
vi.mock('@/components/shared/SEOHead', () => ({ default: () => null }));
vi.mock('@/store/authStore', () => ({ useAuthStore: (selector: (s: unknown) => unknown) => selector({ role: 'editor' }) }));
vi.mock('@/lib/budgets', () => ({ listBudgets: vi.fn(), saveBudget: vi.fn() }));

const saved: SavedBudget = { id: 'budget-id', created_at: '2026-09-28T12:00:00Z', method: 'manual_task_budget_v1',
  inputs: { project_name: 'Release', contingency_pct: '10', tasks: [{ name: 'Build', low_hours: '10', likely_hours: '20', high_hours: '30', hourly_rate_usd: '75' }] },
  totals: { low_hours: '10', likely_hours: '20', high_hours: '30', low_cost_usd: '825.00', likely_cost_usd: '1650.00', high_cost_usd: '2475.00' } };
function fill() {
  for (const [label, value] of [['Project name', 'Release'], ['Contingency (%)', '10'], ['Task name', 'Build'],
    ['Low hours', '10'], ['Likely hours', '20'], ['High hours', '30'], ['Rate (USD/hour)', '75']]) {
    fireEvent.change(screen.getByLabelText(label), { target: { value } });
  }
}
beforeEach(() => { vi.clearAllMocks(); vi.mocked(listBudgets).mockResolvedValue([]); vi.mocked(saveBudget).mockResolvedValue(saved); });
describe('Manual budget planner', () => {
  it('saves explicit assumptions and displays the server calculation', async () => {
    render(<BudgetPage />); fill();
    fireEvent.click(screen.getByRole('button', { name: 'Calculate and save budget' }));
    const result = await screen.findByRole('region', { name: 'Saved budget result' });
    expect(within(result).getByText('$1,650.00')).toBeInTheDocument();
    expect(saveBudget).toHaveBeenCalledWith(saved.inputs);
    expect(screen.getByText(/not an AI prediction/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Likely hours'), { target: { value: '25' } });
    expect(screen.queryByRole('region', { name: 'Saved budget result' })).not.toBeInTheDocument();
  });
  it('rejects inverted ranges without a network request', async () => {
    render(<BudgetPage />); fill();
    fireEvent.change(screen.getByLabelText('Low hours'), { target: { value: '21' } });
    fireEvent.click(screen.getByRole('button', { name: 'Calculate and save budget' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('low hours must be no greater');
    expect(saveBudget).not.toHaveBeenCalled();
  });
  it('preserves inputs after save failure and supports retry', async () => {
    vi.mocked(saveBudget).mockRejectedValueOnce(new Error('offline'));
    render(<BudgetPage />); fill();
    fireEvent.click(screen.getByRole('button', { name: 'Calculate and save budget' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Your inputs are still here');
    expect(screen.getByLabelText('Project name')).toHaveValue('Release');
    fireEvent.click(screen.getByRole('button', { name: 'Calculate and save budget' }));
    expect(await screen.findByRole('region', { name: 'Saved budget result' })).toBeInTheDocument();
  });
  it('opens persisted assumptions and recovers from list failure', async () => {
    vi.mocked(listBudgets).mockRejectedValueOnce(new Error('offline')).mockResolvedValue([saved]);
    render(<BudgetPage />);
    fireEvent.click(await screen.findByRole('button', { name: 'Retry loading budgets' }));
    const button = await screen.findByRole('button', { name: /Release.*1,650/ });
    fireEvent.click(button);
    expect(await screen.findByRole('region', { name: 'Saved budget result' })).toBeInTheDocument();
    await waitFor(() => expect(listBudgets).toHaveBeenCalledTimes(2));
  });
});
