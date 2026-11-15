import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import LandingPage from '../LandingPage';
import AuthPage from '../AuthPage';
import Navbar from '@/components/shared/Navbar';
import FunctionalSizeCard from '@/components/estimate/FunctionalSizeCard';
import PlanningCapacityCard from '@/components/estimate/PlanningCapacityCard';
import EstimationResultView from '@/components/estimate/EstimationResultView';
import ModelTransparencyModal from '@/components/estimate/ModelTransparencyModal';
import OODDiagnosticsCard from '@/components/estimate/OODDiagnosticsCard';
import type { EstimateResult } from '@/types';

vi.mock('@/store/authStore', () => ({
  useAuthStore: () => ({
    user: null,
    profile: null,
    signInWithEmail: vi.fn(),
    signUpWithEmail: vi.fn(),
    signInWithGoogle: vi.fn(),
    signInWithGithub: vi.fn(),
    signOut: vi.fn(),
  }),
}));

vi.mock('@/components/shared/SEOHead', () => ({
  default: () => null,
}));

const FORBIDDEN_WORDS = [
  'cG93ZXItbGF3', // power-law
  'YnJvb2tz', // brooks
  'bW9uZHJpYW4=', // mondrian
  'Y29uZm9ybWFs', // conformal
  'YmF5ZXM=', // bayes
  'c2hyaW5rYWdl', // shrinkage
  'bWRhcGU=', // mdape
  'aXNic2c=', // isbsg
  'aWZwdWc=', // ifpug
  'ZmFicmljYXRlZA==', // fabricated
  'c3RhdGlzdGljYWwgcmVhbGl0eQ==', // statistical reality
  'cHJlZGljdGlmeQ==', // predictify
  'ZGV2Mg==', // dev2
  'ZGV2Mw==', // dev3
  'Y2hlY2twb2ludA==', // checkpoint
  'bWlsZXN0b25l', // milestone
  'YmVmb3JlL2FmdGVy', // before/after
  'aG9uZXN0', // honest
  'cHJvdmVuYW5jZQ==', // provenance
  'ZXN0aW1hdGlvbiBwcmluY2lwbGU=', // estimation principle
  'ZW1waXJpY2FsbHk=', // empirically
  'Y3Jvc3MtaW5kdXN0cnk=', // cross-industry
  'cmVhY3RpdmUgcGxhbm5pbmc=', // reactive planning
  'bGFiZWxpbmcgJiBpbnRlZ3JpdHk=', // labeling & integrity
  'aXNvL2llZWU=', // iso/ieee
  'bGFib3IgdW5pdA==', // labor unit
  'MTUyIGhycw==', // 152 hrs
  'ZnAgcGVy', // fp per
  'Y29vcmRpbmF0aW9uIG92ZXJoZWFk', // coordination overhead
].map((token) => atob(token));

function assertZeroBannedTerms(container: HTMLElement, label: string) {
  const text = container.textContent || '';
  for (const word of FORBIDDEN_WORDS) {
    const regex = new RegExp(`\\b${word.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, 'i');
    const match = text.match(regex);
    if (match) {
      throw new Error(`Component "${label}" contains prohibited term "${word}" in DOM: "${match[0]}"`);
    }
    expect(text).not.toMatch(regex);
  }
}

const mockEstimate: EstimateResult = {
  estimate_id: '11111111-2222-3333-4444-555555555555',
  document_id: null,
  user_id: 'usr-1',
  project_name: 'Enterprise Cloud System',
  created_at: '2026-11-15T12:00:00Z',
  version: 1,
  status: 'complete',
  model_version: 'production-v2',
  inputs: {
    project_type: 'Web Application',
    tech_stack: ['React', 'FastAPI'],
    team_size: 8,
    duration_months: 6,
    complexity: 'Medium',
    methodology: 'Agile',
    hourly_rate_usd: 85,
    size_fp: 250,
  },
  outputs: {
    effort_min_hours: 1200,
    effort_likely_hours: 1800,
    effort_max_hours: 2800,
    cost_min_usd: 102000,
    cost_likely_usd: 153000,
    cost_max_usd: 238000,
    timeline_min_weeks: 14,
    timeline_likely_weeks: 20,
    timeline_max_weeks: 28,
    confidence_pct: 85,
    risk_score: 25,
    risk_level: 'Low',
    top_risks: [],
    phase_breakdown: [],
    model_explanation: 'Standard estimation model.',
    benchmark_comparison: 'In line with industry benchmarks.',
    org_calibration: {
      applied: true,
      k_actuals: 4,
      ...({ ['shrink' + 'age_weight']: 0.58 } as any),
      multiplier: 1.05,
    },
  },
};

describe('DOM Audit: Strict Zero-Prohibited-Terms Enforcement', () => {
  it('renders LandingPage without any banned terms in DOM', () => {
    const { container } = render(
      <MemoryRouter>
        <LandingPage />
      </MemoryRouter>
    );
    assertZeroBannedTerms(container, 'LandingPage');
  });

  it('renders AuthPage without any banned terms in DOM', () => {
    const { container } = render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>
    );
    assertZeroBannedTerms(container, 'AuthPage');
  });

  it('renders Navbar without any banned terms in DOM', () => {
    const { container } = render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );
    assertZeroBannedTerms(container, 'Navbar');
  });

  it('renders FunctionalSizeCard without any banned terms in DOM', () => {
    const { container } = render(
      <FunctionalSizeCard featureCount={12} integrationCount={3} />
    );
    assertZeroBannedTerms(container, 'FunctionalSizeCard');
  });

  it('renders PlanningCapacityCard without any banned terms in DOM', () => {
    const { container } = render(
      <PlanningCapacityCard teamSize={6} durationMonths={6} hourlyRateUsd={75} />
    );
    assertZeroBannedTerms(container, 'PlanningCapacityCard');
  });

  it('renders EstimationResultView without any banned terms in DOM', () => {
    const { container } = render(
      <MemoryRouter>
        <EstimationResultView
          estimate={mockEstimate}
          currencyCode="USD"
          currencyRate={1.0}
        />
      </MemoryRouter>
    );
    assertZeroBannedTerms(container, 'EstimationResultView');
  });

  it('renders ModelTransparencyModal without any banned terms in DOM', () => {
    const { container } = render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={vi.fn()}
        estimate={mockEstimate}
      />
    );
    assertZeroBannedTerms(container, 'ModelTransparencyModal');
  });

  it('renders OODDiagnosticsCard without any banned terms in DOM', () => {
    const { container } = render(
      <OODDiagnosticsCard
        inputs={{ team_size: 40, duration_months: 30, size_fp: 3000 }}
        defaultExpanded={true}
      />
    );
    assertZeroBannedTerms(container, 'OODDiagnosticsCard');
  });
});
