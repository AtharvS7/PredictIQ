import type { EstimateInputs } from '@/types';

export const HOURS_PER_PERSON_MONTH = 152;

/**
 * Converts effort hours to person-months at the standard 152 hrs/PM rate.
 */
export function hoursToPersonMonths(hours: number): { pm: number; formatted: string } {
  if (!Number.isFinite(hours) || hours < 0) {
    return { pm: 0, formatted: '0.0 PM' };
  }
  const pm = hours / HOURS_PER_PERSON_MONTH;
  return {
    pm: Math.round(pm * 10) / 10,
    formatted: `${pm.toFixed(1)} PM`,
  };
}

export interface TierProvenanceDetails {
  tier: 'A' | 'B' | 'C';
  name: string;
  badgeLabel: string;
  subtext: string;
  description: string;
  coverage: string;
  sources: string[];
}

export const TIER_PROVENANCE: Record<'A' | 'B' | 'C', TierProvenanceDetails> = {
  A: {
    tier: 'A',
    name: 'Tier A: Certified Benchmark',
    badgeLabel: 'Tier A',
    subtext: 'Certified Benchmark',
    description:
      'Gold-standard dataset validated against ISBSG cross-organization repositories with split-conformal calibration.',
    coverage: '90% conformal empirical coverage guarantee on in-distribution scope',
    sources: ['ISBSG Repository R2024', 'Certified Project Audits', 'IFPUG 4.3.1 Sizing'],
  },
  B: {
    tier: 'B',
    name: 'Tier B: Validated Standard',
    badgeLabel: 'Tier B',
    subtext: 'Validated Standard',
    description:
      'Empirical project history with statistically validated regression bounds and conformal uncertainty intervals.',
    coverage: '80% confidence interval (p10–p90) with residual variance modeling',
    sources: ['Cross-Industry Engineering Benchmarks', 'Verified Delivery Telemetry'],
  },
  C: {
    tier: 'C',
    name: 'Tier C: Heuristic',
    badgeLabel: 'Tier C',
    subtext: 'Heuristic',
    description:
      'Algorithmic baseline approximation using parametric heuristics. Not calibrated with formal conformal bounds.',
    coverage: 'Uncalibrated baseline — wide uncertainty buffers advised',
    sources: ['Parametric Heuristic Estimator', 'Reference Guidelines'],
  },
};

/**
 * Determines data quality tier based on model version and project scope inputs.
 */
export function determineDataQualityTier(
  modelVersion?: string,
  inputs?: Partial<EstimateInputs>
): 'A' | 'B' | 'C' {
  if (!modelVersion) return 'C';
  const clean = modelVersion.toLowerCase();
  if (clean.startsWith('heuristic') || clean === '1') {
    return 'C';
  }
  if (clean.startsWith('production-v3-')) {
    if (inputs?.size_fp && inputs.size_fp > 0 && inputs.size_fp <= 1500) {
      return 'A';
    }
    return 'B';
  }
  return 'B';
}

export interface OODCheckResult {
  isOOD: boolean;
  reasons: string[];
}

/**
 * Validates whether project inputs fall outside the calibrated empirical distribution.
 */
export function checkIsOOD(inputs?: Partial<EstimateInputs>): OODCheckResult {
  if (!inputs) return { isOOD: false, reasons: [] };
  const reasons: string[] = [];

  if (typeof inputs.team_size === 'number' && inputs.team_size > 30) {
    reasons.push(
      `Planned team size of ${inputs.team_size} exceeds the calibrated benchmark envelope (max 30 engineers). Non-linear Brooks' Law communication overhead applies.`
    );
  }
  if (typeof inputs.duration_months === 'number' && inputs.duration_months > 24) {
    reasons.push(
      `Planned target duration of ${inputs.duration_months} months exceeds single-phase empirical horizons (max 24 months).`
    );
  }
  if (typeof inputs.size_fp === 'number' && inputs.size_fp > 2000) {
    reasons.push(
      `Functional size of ${inputs.size_fp.toLocaleString()} FP is beyond standard calibrated cluster envelopes (max 2,000 FP).`
    );
  }
  if (typeof inputs.integration_count === 'number' && inputs.integration_count > 10) {
    reasons.push(
      `High external integration density (${inputs.integration_count} interfaces) exceeds typical single-phase baseline.`
    );
  }

  return {
    isOOD: reasons.length > 0,
    reasons,
  };
}

/**
 * Derives approximate Function Points from feature and integration counts.
 * Uses IFPUG standard heuristic: ~8 FP per feature user story + 5 FP per external integration.
 */
export function estimateFunctionPoints(featureCount: number, integrationCount: number): number {
  const safeFeatures = Math.max(0, featureCount || 0);
  const safeIntegrations = Math.max(0, integrationCount || 0);
  return Math.round(safeFeatures * 8 + safeIntegrations * 5);
}
