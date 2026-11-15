import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, expect, it, vi } from 'vitest';
import AuthPage from '../AuthPage';

const state = vi.hoisted(() => ({
  session: null as any,
  loading: false,
  signIn: vi.fn(),
  signUp: vi.fn(),
  signInWithOAuth: vi.fn(),
  resetPassword: vi.fn(),
}));

vi.mock('@/store/authStore', () => ({ useAuthStore: () => state }));
vi.mock('@/App', () => ({ useToast: () => ({ addToast: vi.fn() }) }));
vi.mock('@/components/shared/Navbar', () => ({ default: () => <nav data-testid="mock-navbar">Navbar</nav> }));
vi.mock('@/components/shared/SEOHead', () => ({ default: () => null }));

beforeEach(() => {
  vi.resetAllMocks();
  state.session = null;
  state.loading = false;
});

it.each(['Google', 'GitHub'])('keeps %s popup recovery instructions visible and allows retry', async (provider) => {
  state.signInWithOAuth.mockRejectedValue(new Error('Allow pop-ups for this site, then try again.'));
  render(
    <MemoryRouter>
      <AuthPage />
    </MemoryRouter>
  );
  fireEvent.click(screen.getByRole('button', { name: provider }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Allow pop-ups');
  state.signInWithOAuth.mockResolvedValue(undefined);
  fireEvent.click(screen.getByRole('button', { name: provider }));
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(state.signInWithOAuth).toHaveBeenCalledTimes(2);
});

it('disables all sign-in actions during an active request', () => {
  state.loading = true;
  render(
    <MemoryRouter>
      <AuthPage />
    </MemoryRouter>
  );
  for (const name of ['Google', 'GitHub', 'Processing...']) {
    expect(screen.getByRole('button', { name })).toBeDisabled();
  }
});

it('switches between Sign In and Create Account modes', () => {
  render(
    <MemoryRouter>
      <AuthPage />
    </MemoryRouter>
  );

  // Starts in login mode
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Welcome back');
  expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();

  // Click Sign up button
  fireEvent.click(screen.getByRole('button', { name: 'Sign up' }));
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Create account');
  expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();

  // Click Sign in button to return
  fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Welcome back');
});

it('opens in register mode when ?mode=register query param is provided', () => {
  render(
    <MemoryRouter initialEntries={['/auth?mode=register']}>
      <AuthPage />
    </MemoryRouter>
  );
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Create account');
  expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
});

it('redirects authenticated session to dashboard or redirect param', () => {
  state.session = { user: { id: 'u1', email: 'test@example.com' } };

  render(
    <MemoryRouter initialEntries={['/auth?redirect=%2Festimate%2Fnew']}>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/estimate/new" element={<div>Destination Page</div>} />
        <Route path="/dashboard" element={<div>Dashboard Page</div>} />
      </Routes>
    </MemoryRouter>
  );

  expect(screen.getByText('Destination Page')).toBeInTheDocument();
});
