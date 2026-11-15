import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
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
      model_explanation: 'Calibrated estimation.',
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

  it('displays full engine provenance, primary architectures, and mathematical formulations', () => {
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={vi.fn()}
        modelVersion="production-v2"
        tier="A"
      />
    );

    // Header and titles
    expect(screen.getByText(/How This Estimate Works: Engine Provenance & Methodology/i)).toBeInTheDocument();

    // Primary Architecture formulations
    expect(screen.getByText(/Parametric Effort Model/i)).toBeInTheDocument();
    expect(screen.getByText(/Effort = a · Size/i)).toBeInTheDocument();
    expect(screen.getByText(/Staffing & Schedule Dynamics/i)).toBeInTheDocument();
  });

  it('displays formal statement on elimination of subjective multipliers and empirical grounding', () => {
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    // Grounding statement
    expect(screen.getByText(/Empirically Grounded Features & Rigorous Verification/i)).toBeInTheDocument();
    expect(screen.getByText(/No Subjective Multipliers/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Cross-Validation/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Verified Inputs Only/i)).toBeInTheDocument();
  });

  it('cites all 6 empirical benchmark repository sources totaling 915 projects', () => {
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    // Cited Benchmark Repositories
    expect(screen.getByText(/Cited Empirical Benchmark Repositories/i)).toBeInTheDocument();
    expect(screen.getByText(/Industry Cross-Org Benchmarks/i)).toBeInTheDocument();
    expect(screen.getByText(/400 projects/i)).toBeInTheDocument();

    expect(screen.getByText(/NASA Systems Engineering/i)).toBeInTheDocument();
    expect(screen.getByText(/244 projects/i)).toBeInTheDocument();

    expect(screen.getByText(/AT&T Telemetry/i)).toBeInTheDocument();
    expect(screen.getByText(/104 projects/i)).toBeInTheDocument();

    expect(screen.getByText(/Desharnais Benchmark/i)).toBeInTheDocument();
    expect(screen.getByText(/81 projects/i)).toBeInTheDocument();

    expect(screen.getByText(/Maxwell Aerospace & Commercial/i)).toBeInTheDocument();
    expect(screen.getByText(/62 projects/i)).toBeInTheDocument();

    expect(screen.getByText(/Albrecht Pioneer Repository/i)).toBeInTheDocument();
    expect(screen.getByText(/24 projects/i)).toBeInTheDocument();
  });

  it('explains calibrated prediction intervals and stratified size bucketing', () => {
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText(/Calibration Method: Empirically Calibrated Prediction Intervals/i)).toBeInTheDocument();
    expect(screen.getByText(/80% Nominal Empirical Coverage \(p10–p90\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Stratified Size Partitioning/i)).toBeInTheDocument();
    expect(screen.getByText(/Labor Conversion Standard: 152 Productive Hours = 1 Person-Month/i)).toBeInTheDocument();
  });

  it('allows copying contract payload to clipboard and inspecting JSON schema', async () => {
    const mockEstimate = createMockEstimate();
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    });

    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={vi.fn()}
        estimate={mockEstimate}
      />
    );

    // Contract preview toggle
    const inspectButton = screen.getByText(/Inspect JSON Schema/i);
    expect(inspectButton).toBeInTheDocument();
    await act(async () => {
      fireEvent.click(inspectButton);
    });

    expect(screen.getByTestId('contract-json-preview')).toBeInTheDocument();

    // Copy contract payload
    const copyButton = screen.getByTestId('copy-contract-button');
    await act(async () => {
      fireEvent.click(copyButton);
    });

    expect(writeTextMock).toHaveBeenCalledTimes(1);
    const copiedText = writeTextMock.mock.calls[0][0];
    expect(copiedText).toContain('11111111-2222-3333-4444-555555555555');
    expect(copiedText).toContain('Quantum Portal Enterprise');
  });

  it('triggers onClose when close button, done button, or escape key is pressed', () => {
    const onCloseMock = vi.fn();
    render(
      <ModelTransparencyModal
        isOpen={true}
        onClose={onCloseMock}
      />
    );

    const closeBtn = screen.getByTestId('modal-close-button');
    fireEvent.click(closeBtn);
    expect(onCloseMock).toHaveBeenCalledTimes(1);

    const doneBtn = screen.getByText('Done');
    fireEvent.click(doneBtn);
    expect(onCloseMock).toHaveBeenCalledTimes(2);

    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onCloseMock).toHaveBeenCalledTimes(3);
  });
});
