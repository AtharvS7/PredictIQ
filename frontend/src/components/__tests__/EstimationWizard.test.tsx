import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NewEstimatePage from '@/pages/NewEstimatePage';
import { createManualEstimate, exportPDF, exportJSON } from '@/lib/api';

const { addToast } = vi.hoisted(() => ({ addToast: vi.fn() }));
vi.mock('@/App', () => ({ useToast: () => ({ addToast }) }));
vi.mock('@/components/shared/Navbar', () => ({ default: () => <nav>Navbar</nav> }));
vi.mock('@/components/shared/Sidebar', () => ({ default: () => <aside>Sidebar</aside> }));
vi.mock('@/components/shared/CurrencySelector', () => ({ default: () => <div>CurrencySelector</div> }));

vi.mock('@/store/authStore', () => ({
  useAuthStore: () => ({
    user: { uid: 'test-user-123' },
    profile: { full_name: 'Test Engineer', hourly_rate_usd: 80, currency: 'USD' },
  }),
}));

vi.mock('@/store/currencyStore', () => {
  const store = {
    currency: 'USD',
    getRate: () => 1,
    symbol: () => '$',
    format: (v: number) => `$${Math.round(v).toLocaleString()}`,
    convert: (v: number) => v,
  };
  return {
    useCurrencyStore: Object.assign(
      (selector: (s: typeof store) => unknown) => selector(store),
      { getState: () => store }
    ),
  };
});

vi.mock('@/lib/api', () => ({
  createManualEstimate: vi.fn(),
  uploadDocumentFile: vi.fn(),
  analyzeEstimate: vi.fn(),
  extractDocumentParams: vi.fn(),
  exportPDF: vi.fn(),
  exportJSON: vi.fn(),
  createShareLink: vi.fn(),
  duplicateEstimate: vi.fn(),
}));

const mockGeneratedEstimate = {
  estimate_id: 'wizard-est-456',
  document_id: null,
  user_id: 'test-user-123',
  project_name: 'Fintech Mobile Core',
  created_at: '2026-11-06T12:00:00Z',
  version: 1,
  status: 'complete',
  model_version: 'production-v3-0bea59fe789',
  inputs: {
    project_type: 'Mobile App',
    tech_stack: ['React Native', 'TypeScript'],
    team_size: 4,
    duration_months: 5,
    complexity: 'Medium',
    methodology: 'Agile',
    hourly_rate_usd: 80,
    feature_count: 12,
    integration_count: 2,
    volatility_score: 3,
    team_experience: 2,
    size_fp: 106,
  },
  outputs: {
    effort_min_hours: 480,
    effort_likely_hours: 608,
    effort_max_hours: 760,
    cost_min_usd: 38400,
    cost_likely_usd: 48640,
    cost_max_usd: 60800,
    timeline_min_weeks: 10,
    timeline_likely_weeks: 14,
    timeline_max_weeks: 18,
    confidence_pct: 88,
    risk_score: 28,
    risk_level: 'Low' as const,
    top_risks: [],
    phase_breakdown: [
      { phase: 'Phase 1', effort_hours: 608, cost_usd: 48640, duration_weeks: 14, pct_of_total: 100 },
    ],
    model_explanation: 'Standard mobile app estimation.',
    benchmark_comparison: 'Within 50th percentile of ISBSG mobile projects.',
  },
};

describe('Estimation Wizard Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('navigates through Step 1 (Scope & Functional Size) to Step 2 (Planning Parameters)', () => {
    render(
      <MemoryRouter>
        <NewEstimatePage />
      </MemoryRouter>
    );

    // Step 1: Requirements & Functional Size
    expect(screen.getByText('Functional Size & Scope Calibration')).toBeInTheDocument();
    expect(screen.getByText(/Upload Specification or Enter Requirements/i)).toBeInTheDocument();

    // Advance to Step 2 via manual entry
    const manualBtn = screen.getByRole('button', { name: /enter parameters manually/i });
    fireEvent.click(manualBtn);

    // Step 2: Planning Parameters
    expect(screen.getByText('Planning Parameters & Capacity Target')).toBeInTheDocument();
    expect(screen.getByLabelText('Project Name')).toBeInTheDocument();
    expect(screen.getByLabelText(/Planned Target Duration/i)).toBeInTheDocument();
  });

  it('completes the entire flow through Step 3 (Calibrated Results)', async () => {
    vi.mocked(createManualEstimate).mockResolvedValue({
      data: mockGeneratedEstimate,
    } as Awaited<ReturnType<typeof createManualEstimate>>);

    render(
      <MemoryRouter>
        <NewEstimatePage />
      </MemoryRouter>
    );

    // Go to Step 2
    fireEvent.click(screen.getByRole('button', { name: /enter parameters manually/i }));

    // Fill in Step 2 parameters
    fireEvent.change(screen.getByLabelText('Project Name'), { target: { value: 'Fintech Mobile Core' } });
    fireEvent.change(screen.getByLabelText('Team Size'), { target: { value: '4' } });

    // Submit form to generate estimate
    const generateBtn = screen.getByRole('button', { name: /generate estimate/i });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(createManualEstimate).toHaveBeenCalled();
    });

    // Step 3: Result View
    expect(await screen.findByText('Calibrated Effort Ranges')).toBeInTheDocument();

    // 608 hrs / 152 = 4.0 PM
    expect(screen.getAllByText(/608 hrs/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/4\.0 PM person-months/i)).toBeInTheDocument();

    // Data Quality Tier Badge
    expect(screen.getByText('Tier A')).toBeInTheDocument();

    // Export buttons are available
    expect(screen.getByRole('button', { name: /Export JSON/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /PDF/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Share/i })).toBeInTheDocument();
  });
});
