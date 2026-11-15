import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ModelTransparencyModal from '../estimate/ModelTransparencyModal';
import type { EstimateResult } from '@/types';

function createMockEstimate(): EstimateResult {
  return {
    estimate_id: '11111111-2222-3333-4444-555555555555',
    document_id: null,
    user_id: 'user-123',
    project_name: 'Quantum Portal Enterprise',
    created_at: '2026-11-06T10:00:00Z',
    version: 1,
    status: 'complete',
    model_version: 'production-v2',
    inputs: {
      project_type: 'Web Application',
      tech_stack: ['React', 'FastAPI'],
      team_size: 6,
      duration_months: 6,
      complexity: 'Medium',
      methodology: 'Agile',
      hourly_rate_usd: 85,
      size_fp: 185,
    },
    outputs: {
      effort_min_hours: 1150,
      effort_likely_hours: 1820,
      effort_max_hours: 2940,
      cost_min_usd: 97750,
      cost_likely_usd: 154700,
      cost_max_usd: 249900,
      timeline_min_weeks: 14,
      timeline_likely_weeks: 20,
      timeline_max_weeks: 26,
      confidence_pct: 85,
      risk_score: 28,
      risk_level: 'Low',
      top_risks: [],
      phase_breakdown: [],
      model_explanation: 'Estimation based on historical data.',
      benchmark_comparison: 'In line with industry datasets.',
    },
  };
}

describe('ModelTransparencyModal Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing when isOpen is false', () => {
    const { container } = render(
      <ModelTransparencyModal
        isOpen={false}
        onClose={vi.fn()}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('displays clean 3-sentence about modal when isOpen is true', () => {
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={vi.fn()}
        estimate={createMockEstimate()}
      />
    );

    // Modal title
    expect(screen.getByText('About this estimate')).toBeInTheDocument();

    // 3 clean sentences
    expect(
      screen.getByText(/This estimate is based on data from 915 real software projects\./i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/The likely range covers most outcomes; the wider range covers almost all\./i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Add your completed projects in Settings to adjust estimates to your team\./i)
    ).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={onClose}
      />
    );

    fireEvent.click(screen.getByTestId('modal-close-button'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Done button is clicked', () => {
    const onClose = vi.fn();
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={onClose}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /Done/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
