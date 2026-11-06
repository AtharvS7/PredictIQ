import { describe, it, expect, vi } from 'vitest';
import {
  formatEstimateToV2Contract,
  validateV2Contract,
  ensureValidUUID,
  deriveEstimateDrivers,
  deriveEstimateAssumptions,
} from '../estimate/exportContractUtils';
import type { EstimateResult } from '@/types';

function createMockEstimate(overrides: Partial<EstimateResult> = {}): EstimateResult {
  return {
    estimate_id: '11111111-2222-3333-4444-555555555555',
    document_id: null,
    user_id: 'user-001',
    project_name: 'Healthcare Claims Portal',
    created_at: '2026-11-06T10:00:00Z',
    version: 1,
    status: 'complete',
    model_version: '2.0.0-rc.1',
    inputs: {
      project_type: 'Enterprise Healthcare',
      tech_stack: ['FastAPI', 'React', 'PostgreSQL'],
      team_size: 8,
      duration_months: 6,
      complexity: 'High',
      methodology: 'Agile',
      hourly_rate_usd: 75,
      feature_count: 38,
      integration_count: 5,
      size_fp: 185,
    },
    outputs: {
      effort_min_hours: 1150,
      effort_likely_hours: 1820,
      effort_max_hours: 2940,
      cost_min_usd: 86250,
      cost_likely_usd: 136500,
      cost_max_usd: 220500,
      timeline_min_weeks: 14,
      timeline_likely_weeks: 20,
      timeline_max_weeks: 28,
      confidence_pct: 85,
      risk_score: 30,
      risk_level: 'Low',
      top_risks: [],
      phase_breakdown: [],
      model_explanation: 'Standard calibrated power-law model.',
      benchmark_comparison: 'Consistent with cross-organization empirical databases.',
    },
    ...overrides,
  };
}

describe('Export Flows & Contract Integrity (api_estimate_v2.json)', () => {
  it('normalizes legacy IDs to valid RFC 4122 UUID strings', () => {
    const valid = '11111111-2222-3333-4444-555555555555';
    expect(ensureValidUUID(valid)).toBe(valid);

    const legacy = 'est-12345678-abcd';
    const normalized = ensureValidUUID(legacy);
    expect(normalized).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/);
  });

  it('formats EstimateResult into a compliant PredictIQEstimateResponseV2 payload', () => {
    const estimate = createMockEstimate();
    const contract = formatEstimateToV2Contract(estimate, 'USD', 1);

    expect(contract.estimate_id).toBe('11111111-2222-3333-4444-555555555555');
    expect(contract.project_name).toBe('Healthcare Claims Portal');

    // Quantile effort hours
    expect(contract.effort_hours).toEqual({
      p10: 1150,
      p50: 1820,
      p90: 2940,
    });

    // Person-months at 152 hrs/PM
    expect(contract.person_months.p10).toBeCloseTo(1150 / 152, 1);
    expect(contract.person_months.p50).toBeCloseTo(1820 / 152, 1);
    expect(contract.person_months.p90).toBeCloseTo(2940 / 152, 1);

    // Cost
    expect(contract.cost).toEqual({
      p10: 86250,
      p50: 136500,
      p90: 220500,
      currency: 'USD',
      rate: 75,
    });

    // Size
    expect(contract.size.value).toBe(185);
    expect(contract.size.source).toBe('user');
    expect(contract.size.uncertainty.p50).toBe(185);

    // Model metadata
    expect(contract.model.sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(contract.model.trained_on_rows).toBe(915);
    expect(contract.model.sources).toContain('china');
    expect(contract.model.sources).toContain('kitchenham');
  });

  it('validates strictly against docs/contracts/api_estimate_v2.json requirements', () => {
    const estimate = createMockEstimate();
    const contract = formatEstimateToV2Contract(estimate, 'EUR', 0.92);

    const validation = validateV2Contract(contract);
    expect(validation.isValid).toBe(true);
    expect(validation.errors).toHaveLength(0);
  });

  it('catches violations when fields are missing or improperly formatted', () => {
    const invalidPayload = {
      estimate_id: 'not-a-uuid',
      project_name: '',
      effort_hours: { p10: -10, p50: 100 }, // missing p90, negative p10
      cost: { currency: 'INVALID' },
      data_quality_tier: 'Z',
    };

    const validation = validateV2Contract(invalidPayload);
    expect(validation.isValid).toBe(false);
    expect(validation.errors.some((e) => e.includes('Invalid UUID format'))).toBe(true);
    expect(validation.errors.some((e) => e.includes('project_name must be a non-empty string'))).toBe(true);
    expect(validation.errors.some((e) => e.includes('data_quality_tier'))).toBe(true);
  });

  it('correctly sets data_quality_tier and ood_flags for extreme scopes', () => {
    const oodEstimate = createMockEstimate({
      inputs: {
        project_type: 'Mega Platform',
        tech_stack: ['Java'],
        team_size: 40,
        duration_months: 30,
        complexity: 'High',
        methodology: 'Agile',
        hourly_rate_usd: 90,
        size_fp: 3000,
      },
    });

    const contract = formatEstimateToV2Contract(oodEstimate);
    expect(contract.ood_flags.length).toBeGreaterThan(0);
    expect(contract.ood_flags.some((f) => f.includes('team size of 40'))).toBe(true);
    expect(contract.ood_flags.some((f) => f.includes('3,000 FP'))).toBe(true);

    const validation = validateV2Contract(contract);
    expect(validation.isValid).toBe(true);
  });
});
