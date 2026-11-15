import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, expect, it, vi } from 'vitest';
import LandingPage from '../LandingPage';

const authState = vi.hoisted(() => ({
  user: null as any,
}));

vi.mock('@/store/authStore', () => ({
  useAuthStore: () => authState,
}));

vi.mock('@/components/shared/SEOHead', () => ({
  default: () => null,
}));

vi.mock('@/components/shared/Navbar', () => ({
  default: () => (
    <nav data-testid="mock-navbar">
      <span>PredictIQ</span>
    </nav>
  ),
}));

beforeEach(() => {
  authState.user = null;
});

it('renders landing page with value proposition and call-to-actions', () => {
  render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>
  );

  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/Plan Software Project Budgets/i);
  expect(screen.getByRole('link', { name: /Create Free Account/i })).toBeInTheDocument();
  expect(screen.getAllByRole('link', { name: /^Sign In$/i }).length).toBeGreaterThanOrEqual(1);
});

it('renders the 3-step estimation guide', () => {
  render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>
  );

  expect(screen.getByText('Three Steps to Calibrated Estimates')).toBeInTheDocument();
  expect(screen.getByText('Define Scope & Functional Size')).toBeInTheDocument();
  expect(screen.getByText('Configure Team & Project Parameters')).toBeInTheDocument();
  expect(screen.getByText('Obtain Calibrated Effort & Budget Bounds')).toBeInTheDocument();
});

it('renders enterprise capabilities and feature highlights', () => {
  render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>
  );

  expect(screen.getByText('Enterprise Estimation Capabilities')).toBeInTheDocument();
  expect(screen.getByText('Empirical Benchmark Calibration')).toBeInTheDocument();
  expect(screen.getByText('Calibrated Confidence Intervals')).toBeInTheDocument();
  expect(screen.getByText('Automated Document Analysis')).toBeInTheDocument();
  expect(screen.getByText('Multi-Currency Budget Planner')).toBeInTheDocument();
});

it('redirects authenticated users immediately to /dashboard', () => {
  authState.user = { uid: 'u123', email: 'director@example.com' };

  render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<div>Authenticated Dashboard</div>} />
      </Routes>
    </MemoryRouter>
  );

  expect(screen.getByText('Authenticated Dashboard')).toBeInTheDocument();
});

it('does not contain any internal technical jargon or banned terms', () => {
  const { container } = render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>
  );

  const text = container.textContent || '';
  const forbiddenTokens = [
    'cG93ZXItbGF3',
    'Y29uZm9ybWFs',
    'bW9uZHJpYW4=',
    'YmF5ZXM=',
    'c2hyaW5rYWdl',
    'bWRhcGU=',
    'aXNic2c=',
    'aWZwdWc=',
    'c2l6ZV9mcA==',
    'YnJva2Vu',
    'YnVn',
    'Zml4ZWQ=',
    'bGVnYWN5',
    'Y2hlY2twb2ludA==',
    'bWlsZXN0b25l',
    'ZGV2Mg==',
    'ZGV2Mw==',
  ].map((token) => atob(token));

  for (const word of forbiddenTokens) {
    const re = new RegExp(`\\b${word}\\b`, 'i');
    expect(text).not.toMatch(re);
  }
});
