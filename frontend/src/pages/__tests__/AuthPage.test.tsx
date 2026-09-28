import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, expect, it, vi } from 'vitest';
import AuthPage from '../AuthPage';

const state = vi.hoisted(() => ({ session: null, loading: false, signInWithOAuth: vi.fn() }));
vi.mock('@/store/authStore', () => ({ useAuthStore: () => state }));
vi.mock('@/App', () => ({ useToast: () => ({ addToast: vi.fn() }) }));
vi.mock('@/components/shared/Navbar', () => ({ default: () => null }));
vi.mock('@/components/shared/SEOHead', () => ({ default: () => null }));

beforeEach(() => { vi.resetAllMocks(); state.loading = false; });

it.each(['Google', 'GitHub'])('keeps %s popup recovery instructions visible and allows retry', async (provider) => {
  state.signInWithOAuth.mockRejectedValue(new Error('Allow pop-ups for this site, then try again.'));
  render(<MemoryRouter><AuthPage /></MemoryRouter>);
  fireEvent.click(screen.getByRole('button', { name: provider, exact: true }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Allow pop-ups');
  state.signInWithOAuth.mockResolvedValue(undefined);
  fireEvent.click(screen.getByRole('button', { name: provider, exact: true }));
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(state.signInWithOAuth).toHaveBeenCalledTimes(2);
});

it('disables all sign-in actions during an active request', () => {
  state.loading = true;
  render(<MemoryRouter><AuthPage /></MemoryRouter>);
  for (const name of ['Google', 'GitHub', 'Processing...']) {
    expect(screen.getByRole('button', { name, exact: true })).toBeDisabled();
  }
});
