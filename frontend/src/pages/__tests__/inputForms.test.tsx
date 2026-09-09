import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import NewEstimatePage from '../NewEstimatePage';
import SettingsPage from '../SettingsPage';

const mocks = vi.hoisted(() => ({ create: vi.fn(), update: vi.fn(), toast: vi.fn(), currency: vi.fn() }));
vi.mock('@/App', () => ({ useToast: () => ({ addToast: mocks.toast }), useTheme: () => ({ theme: 'light' }) }));
vi.mock('@/components/shared/Navbar', () => ({ default: () => null }));
vi.mock('@/components/shared/Sidebar', () => ({ default: () => null }));
vi.mock('@/components/shared/CurrencySelector', () => ({ default: () => null }));
vi.mock('@/store/authStore', () => ({ useAuthStore: () => ({ user: { uid: 'test' }, profile: { full_name: 'Test', hourly_rate_usd: 75, currency: 'USD' }, updateProfile: mocks.update }) }));
vi.mock('@/store/currencyStore', () => ({ useCurrencyStore: Object.assign(
  (select: (state: unknown) => unknown) => select({ currency: 'INR', getRate: () => 80 }),
  { getState: () => ({ setCurrency: mocks.currency }) },
) }));
vi.mock('@/lib/api', () => ({ createManualEstimate: mocks.create, uploadDocumentFile: vi.fn(), analyzeEstimate: vi.fn(), extractDocumentParams: vi.fn() }));

describe('Estimate input contract', () => {
  beforeEach(() => vi.clearAllMocks());
  it('sends USD immediately and preserves inputs when predictions are unavailable', async () => {
    mocks.create.mockRejectedValueOnce({ response: { status: 503 } });
    render(<MemoryRouter><NewEstimatePage /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: /manual/i }));
    fireEvent.change(screen.getByLabelText('Project Name'), { target: { value: 'Rate regression' } });
    const rate = screen.getByLabelText('Hourly Rate (INR/hour)');
    expect(rate).toHaveValue(6000);
    fireEvent.change(rate, { target: { value: '8000' } });
    fireEvent.click(screen.getByRole('button', { name: /generate estimate/i }));
    // A request must already have started, without advancing timers or fake stages.
    expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({ hourly_rate_usd: 100 }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Prediction service is unavailable');
    expect(screen.getByLabelText('Project Name')).toHaveValue('Rate regression');
    expect(screen.getByLabelText('Hourly Rate (INR/hour)')).toHaveValue(8000);
    expect(screen.getByLabelText('External Integrations')).toHaveAttribute('max', '15');
    expect(screen.getByLabelText('Project Name')).toHaveAttribute('maxlength', '200');
  });
});

describe('Settings input contract', () => {
  beforeEach(() => vi.clearAllMocks());
  it.each(['', '0', '501'])('rejects invalid hourly rate %s without silently saving 75', async value => {
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText('Hourly Rate (USD)'), { target: { value } });
    fireEvent.click(screen.getByRole('button', { name: 'Save Changes' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('between 10 and 500 USD');
    expect(mocks.update).not.toHaveBeenCalled();
  });

  it('saves fractional USD rates without changing their currency unit', async () => {
    mocks.update.mockResolvedValueOnce(undefined);
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText('Hourly Rate (USD)'), { target: { value: '125.5' } });
    fireEvent.change(screen.getByLabelText('Display Currency'), { target: { value: 'INR' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save Changes' }));
    await waitFor(() => expect(mocks.update).toHaveBeenCalledWith(expect.objectContaining({ hourly_rate_usd: 125.5, currency: 'INR' })));
    await waitFor(() => expect(mocks.currency).toHaveBeenCalledWith('INR'));
  });
});
