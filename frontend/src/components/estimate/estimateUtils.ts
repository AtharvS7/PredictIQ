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
    name: 'Tier A',
    badgeLabel: 'Tier A',
    subtext: 'Typical size',
    description: 'Typical project size',
    coverage: 'Standard range',
    sources: ['Historical project data'],
  },
  B: {
    tier: 'B',
    name: 'Tier B',
    badgeLabel: 'Tier B',
    subtext: 'From document',
    description: 'Size taken from your document - please review',
    coverage: 'Extracted from document',
    sources: ['Document scope'],
  },
  C: {
    tier: 'C',
    name: 'Tier C',
    badgeLabel: 'Tier C',
    subtext: 'Large scope',
    description: 'Larger than most projects in our data',
    coverage: 'Wider range',
    sources: ['Large scale projects'],
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
 * Validates whether project inputs fall outside the typical distribution.
 */
export function checkIsOOD(inputs?: Partial<EstimateInputs>): OODCheckResult {
  if (!inputs) return { isOOD: false, reasons: [] };
  const reasons: string[] = [];

  if (typeof inputs.team_size === 'number' && inputs.team_size > 30) {
    reasons.push(
      `Planned team size of ${inputs.team_size} exceeds typical team sizes (max 30 engineers).`
    );
  }
  if (typeof inputs.duration_months === 'number' && inputs.duration_months > 24) {
    reasons.push(
      `Planned duration of ${inputs.duration_months} months exceeds typical timelines (max 24 months).`
    );
  }
  if (typeof inputs.size_fp === 'number' && inputs.size_fp > 2000) {
    reasons.push(
      `Project size of ${inputs.size_fp.toLocaleString()} FP is larger than typical projects (max 2,000 FP).`
    );
  }
  if (typeof inputs.integration_count === 'number' && inputs.integration_count > 10) {
    reasons.push(
      `High external integration density (${inputs.integration_count} interfaces) exceeds typical projects.`
    );
  }

  return {
    isOOD: reasons.length > 0,
    reasons,
  };
}

/**
 * Derives approximate Function Points from feature and integration counts.
 */
export function estimateFunctionPoints(featureCount: number, integrationCount: number): number {
  const safeFeatures = Math.max(0, featureCount || 0);
  const safeIntegrations = Math.max(0, integrationCount || 0);
  return Math.round(safeFeatures * 8 + safeIntegrations * 5);
}
