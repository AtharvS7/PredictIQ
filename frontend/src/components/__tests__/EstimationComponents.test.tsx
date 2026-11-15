import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FunctionalSizeCard from '../estimate/FunctionalSizeCard';
import PlanningCapacityCard from '../estimate/PlanningCapacityCard';
import EstimationResultView from '../estimate/EstimationResultView';
import {
  hoursToPersonMonths,
  determineDataQualityTier,
  checkIsOOD,
  estimateFunctionPoints,
} from '../estimate/estimateUtils';
import type { EstimateResult } from '@/types';

function createMockEstimate(overrides: Partial<EstimateResult> = {}): EstimateResult {
  return {
    estimate_id: 'est-12345678-abcd',
    document_id: null,
    user_id: 'user-001',
    project_name: 'Alpha Quantum Platform',
    created_at: '2026-11-06T10:00:00Z',
    version: 1,
    status: 'complete',
    model_version: 'production-v3-0bea59fe789',
    inputs: {
      project_type: 'Web App',
      tech_stack: ['React', 'FastAPI', 'PostgreSQL'],
      team_size: 5,
      duration_months: 6,
      complexity: 'Medium',
      methodology: 'Agile',
      hourly_rate_usd: 80,
      feature_count: 15,
      integration_count: 3,
      volatility_score: 2,
      team_experience: 3,
      size_fp: 135,
    },
    outputs: {
      effort_min_hours: 608,
      effort_likely_hours: 760,
      effort_max_hours: 988,
      cost_min_usd: 48640,
      cost_likely_usd: 60800,
      cost_max_usd: 79040,
      timeline_min_weeks: 12,
      timeline_likely_weeks: 16,
      timeline_max_weeks: 20,
      confidence_pct: 88,
      risk_score: 35,
      risk_level: 'Low',
      top_risks: [
        { name: 'API Latency', description: 'Third-party latency variance', severity: 'Low' },
      ],
      phase_breakdown: [
        { phase: 'Design & Architecture', effort_hours: 152, cost_usd: 12160, duration_weeks: 3, pct_of_total: 20 },
        { phase: 'Core Engineering', effort_hours: 456, cost_usd: 36480, duration_weeks: 10, pct_of_total: 60 },
        { phase: 'QA & Deployment', effort_hours: 152, cost_usd: 12160, duration_weeks: 3, pct_of_total: 20 },
      ],
      model_explanation: 'Prediction driven by 135 Function Points and agile methodology.',
      benchmark_comparison: 'Puts effort at 48th percentile of web benchmark.',
    },
    ...overrides,
  };
}

describe('estimateUtils', () => {
  it('converts hours to person-months at standard 152 hrs/PM', () => {
    expect(hoursToPersonMonths(152)).toEqual({ pm: 1.0, formatted: '1.0 PM' });
    expect(hoursToPersonMonths(760)).toEqual({ pm: 5.0, formatted: '5.0 PM' });
    expect(hoursToPersonMonths(80)).toEqual({ pm: 0.5, formatted: '0.5 PM' });
    expect(hoursToPersonMonths(0)).toEqual({ pm: 0.0, formatted: '0.0 PM' });
    expect(hoursToPersonMonths(-10)).toEqual({ pm: 0.0, formatted: '0.0 PM' });
  });

  it('determines data quality tier correctly', () => {
    expect(determineDataQualityTier('production-v3-abc', { size_fp: 250 })).toBe('A');
    expect(determineDataQualityTier('production-v3-abc', {})).toBe('B');
    expect(determineDataQualityTier('heuristic-v1')).toBe('C');
    expect(determineDataQualityTier('1')).toBe('C');
    expect(determineDataQualityTier('')).toBe('C');
  });

  it('detects Out-Of-Distribution (OOD) parameters', () => {
    expect(checkIsOOD({ team_size: 5, duration_months: 6 }).isOOD).toBe(false);

    const oodTeam = checkIsOOD({ team_size: 45, duration_months: 6 });
    expect(oodTeam.isOOD).toBe(true);
    expect(oodTeam.reasons[0]).toContain('exceeds typical team sizes');

    const oodDuration = checkIsOOD({ team_size: 5, duration_months: 36 });
    expect(oodDuration.isOOD).toBe(true);
    expect(oodDuration.reasons[0]).toContain('exceeds typical timelines');

    const oodFp = checkIsOOD({ size_fp: 3500 });
    expect(oodFp.isOOD).toBe(true);
    expect(oodFp.reasons[0]).toContain('larger than typical projects');
  });

  it('estimates function points with standard heuristic', () => {
    // 10 features * 8 + 2 integrations * 5 = 90 FP
    expect(estimateFunctionPoints(10, 2)).toBe(90);
    expect(estimateFunctionPoints(0, 0)).toBe(0);
  });
});

describe('FunctionalSizeCard Component', () => {
  it('renders Function Point sizing feedback and controls', () => {
    const onFeatureChange = vi.fn();
    const onIntegrationChange = vi.fn();

    render(
      <FunctionalSizeCard
        featureCount={10}
        integrationCount={2}
        onFeatureChange={onFeatureChange}
        onIntegrationChange={onIntegrationChange}
      />
    );

    expect(screen.getAllByText('Project size').length).toBeGreaterThanOrEqual(1);

    // 10 * 8 + 2 * 5 = 90 FP
    expect(screen.getByText('90')).toBeInTheDocument();

    // Test input changes
    const featureInput = screen.getByLabelText(/Number of features/i);
    fireEvent.change(featureInput, { target: { value: '15' } });
    expect(onFeatureChange).toHaveBeenCalledWith(15);

    const integrationInput = screen.getByLabelText(/Number of external integrations/i);
    fireEvent.change(integrationInput, { target: { value: '4' } });
    expect(onIntegrationChange).toHaveBeenCalledWith(4);
  });
});

describe('PlanningCapacityCard Component', () => {
  it('reactively computes capacity in hours and cost', () => {
    render(
      <PlanningCapacityCard
        teamSize={4}
        durationMonths={5}
        hourlyRateUsd={100}
        currencySymbol="$"
        currencyRate={1}
        currencyCode="USD"
      />
    );

    // 4 team * 5 months * 152 hrs = 3,040 hours
    expect(screen.getByText('3,040')).toBeInTheDocument();

    // 3,040 hrs * $100 = $304,000 baseline cost
    expect(screen.getByText('$304,000')).toBeInTheDocument();
  });

  it('renders a team size warning when team size is large (>25)', () => {
    render(
      <PlanningCapacityCard
        teamSize={30}
        durationMonths={6}
        hourlyRateUsd={75}
      />
    );

    expect(screen.getByText(/Team size note:/i)).toBeInTheDocument();
  });
});

describe('EstimationResultView Component', () => {
  it('renders effort ranges in hours and person-months', () => {
    const estimate = createMockEstimate();
    render(<EstimationResultView estimate={estimate} />);

    // 608 hrs / 152 = 4.0 PM
    expect(screen.getAllByText(/608 hrs/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/4\.0 PM/i).length).toBeGreaterThanOrEqual(1);

    expect(screen.getAllByText(/760 hrs/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/5\.0 PM/i).length).toBeGreaterThanOrEqual(1);

    expect(screen.getAllByText(/988 hrs/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/6\.5 PM/i).length).toBeGreaterThanOrEqual(1);

    // Visual confidence range bar exists
    expect(screen.getByRole('group', { name: /Effort range bar/i })).toBeInTheDocument();

    // Tier badge exists
    expect(screen.getByText('Tier A')).toBeInTheDocument();
  });

  it('renders Out-Of-Distribution (OOD) warning when parameters exceed bounds', () => {
    const oodEstimate = createMockEstimate({
      inputs: {
        project_type: 'Web App',
        tech_stack: [],
        team_size: 50,
        duration_months: 30,
        complexity: 'High',
        methodology: 'Agile',
        hourly_rate_usd: 80,
      },
    });

    render(<EstimationResultView estimate={oodEstimate} />);

    expect(screen.getByText(/Large project notice/i)).toBeInTheDocument();
    expect(screen.getByText(/Planned team size of 50 exceeds typical team sizes/i)).toBeInTheDocument();
  });

  it('triggers export and share action callbacks', () => {
    const onExportPDF = vi.fn();
    const onExportJSON = vi.fn();
    const onShare = vi.fn();
    const onDuplicate = vi.fn();

    const estimate = createMockEstimate();
    render(
      <EstimationResultView
        estimate={estimate}
        onExportPDF={onExportPDF}
        onExportJSON={onExportJSON}
        onShare={onShare}
        onDuplicate={onDuplicate}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /PDF/i }));
    expect(onExportPDF).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: /Export JSON/i }));
    expect(onExportJSON).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: /Share/i }));
    expect(onShare).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: /Duplicate/i }));
    expect(onDuplicate).toHaveBeenCalledTimes(1);
  });
});
