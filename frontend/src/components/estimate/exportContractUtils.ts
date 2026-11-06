import type { EstimateResult, EstimateInputs } from '@/types';
import {
  determineDataQualityTier,
  checkIsOOD,
  estimateFunctionPoints,
  hoursToPersonMonths,
} from './estimateUtils';

export interface DriverItemV2 {
  name: string;
  impact: 'major_increase' | 'moderate_increase' | 'neutral' | 'moderate_decrease' | 'major_decrease';
  description: string;
}

export interface AssumptionItemV2 {
  category: string;
  description: string;
  editable: boolean;
}

export interface ModelMetadataV2 {
  version: string;
  sha256: string;
  trained_on_rows: number;
  sources: string[];
  metrics_ref: string;
}

export interface EstimateResponseV2Contract {
  estimate_id: string;
  project_name: string;
  effort_hours: {
    p10: number;
    p50: number;
    p90: number;
  };
  person_months: {
    p10: number;
    p50: number;
    p90: number;
  };
  cost: {
    p10: number;
    p50: number;
    p90: number;
    currency: string;
    rate: number;
  };
  size: {
    value: number;
    source: 'user' | 'nlp';
    uncertainty: {
      p10: number;
      p50: number;
      p90: number;
    };
  };
  drivers: DriverItemV2[];
  assumptions: AssumptionItemV2[];
  data_quality_tier: 'A' | 'B' | 'C';
  ood_flags: string[];
  model: ModelMetadataV2;
}

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const SHA256_REGEX = /^[a-f0-9]{64}$/i;

/**
 * Normalizes any string identifier into a compliant UUID string.
 */
export function ensureValidUUID(id: string): string {
  if (UUID_REGEX.test(id)) {
    return id.toLowerCase();
  }
  // Strip non-hex chars
  const hexOnly = id.replace(/[^0-9a-f]/gi, '').toLowerCase();
  const padded = (hexOnly + '0'.repeat(32)).slice(0, 32);
  return `${padded.slice(0, 8)}-${padded.slice(8, 12)}-${padded.slice(12, 16)}-${padded.slice(16, 20)}-${padded.slice(20, 32)}`;
}

/**
 * Derives contract-compliant drivers from estimate inputs and outputs.
 */
export function deriveEstimateDrivers(
  inputs: EstimateInputs,
  sizeFp: number
): DriverItemV2[] {
  const drivers: DriverItemV2[] = [
    {
      name: 'Functional Size',
      impact: 'major_increase',
      description: `${sizeFp} estimated Function Points derived from project scope specifications.`,
    },
  ];

  if (typeof inputs.integration_count === 'number' && inputs.integration_count > 3) {
    drivers.push({
      name: 'Integration Complexity',
      impact: 'moderate_increase',
      description: `${inputs.integration_count} external integration interfaces detected (API gateways, auth, third-party services).`,
    });
  }

  if (typeof inputs.team_size === 'number' && inputs.team_size > 12) {
    drivers.push({
      name: 'Team Coordination Scale',
      impact: 'moderate_increase',
      description: `Planned team size of ${inputs.team_size} software engineers introduces communication path scaling.`,
    });
  }

  if (inputs.complexity && inputs.complexity.toLowerCase() === 'high') {
    drivers.push({
      name: 'High Technical Complexity',
      impact: 'moderate_increase',
      description: 'High architecture complexity profile with stringent reliability requirements.',
    });
  }

  drivers.push({
    name: 'Modern Architecture Stack',
    impact: 'neutral',
    description: `${inputs.tech_stack?.join(', ') || inputs.project_type || 'Modern Web'} baseline productivity envelope.`,
  });

  return drivers;
}

/**
 * Derives standardized estimation assumptions.
 */
export function deriveEstimateAssumptions(
  hourlyRate: number,
  currencyCode: string = 'USD'
): AssumptionItemV2[] {
  return [
    {
      category: 'Sizing',
      description: 'Functional size uncertainty band reflects ±15% variance from requirements interpretation.',
      editable: true,
    },
    {
      category: 'Effort Conversion',
      description: '152 productive working hours per person-month (standard software labor baseline).',
      editable: false,
    },
    {
      category: 'Hourly Rate',
      description: `Blended engineering rate of ${currencyCode} ${hourlyRate}/hour (editable).`,
      editable: true,
    },
    {
      category: 'Uncertainty Calibration',
      description: 'Split-conformal prediction intervals with Mondrian size bucketing (80% nominal coverage).',
      editable: false,
    },
  ];
}

/**
 * Transforms an EstimateResult into the standardized PredictIQ v2 API contract payload
 * strictly adhering to docs/contracts/api_estimate_v2.json.
 */
export function formatEstimateToV2Contract(
  estimate: EstimateResult,
  currencyCode: string = 'USD',
  currencyRate: number = 1
): EstimateResponseV2Contract {
  const { inputs, outputs, model_version, project_name, estimate_id, document_id } = estimate;

  const validUUID = ensureValidUUID(estimate_id);

  // Functional size determination
  const sizeValue =
    inputs.size_fp && inputs.size_fp > 0
      ? inputs.size_fp
      : estimateFunctionPoints(inputs.feature_count ?? 0, inputs.integration_count ?? 0);

  const sizeSource: 'user' | 'nlp' = document_id ? 'nlp' : (inputs.size_fp ? 'user' : 'nlp');

  // Quantile effort hours
  const p10Hours = Math.round(outputs.effort_min_hours * 10) / 10;
  const p50Hours = Math.round(outputs.effort_likely_hours * 10) / 10;
  const p90Hours = Math.round(outputs.effort_max_hours * 10) / 10;

  // Person-months at 152 hrs/PM
  const p10PM = Math.round(hoursToPersonMonths(p10Hours).pm * 100) / 100;
  const p50PM = Math.round(hoursToPersonMonths(p50Hours).pm * 100) / 100;
  const p90PM = Math.round(hoursToPersonMonths(p90Hours).pm * 100) / 100;

  // Costs converted to active currency
  const rate = currencyRate > 0 ? currencyRate : 1;
  const p10Cost = Math.round(outputs.cost_min_usd * rate * 100) / 100;
  const p50Cost = Math.round(outputs.cost_likely_usd * rate * 100) / 100;
  const p90Cost = Math.round(outputs.cost_max_usd * rate * 100) / 100;

  // Clean 3-character currency
  const cleanCurrency = currencyCode.trim().slice(0, 3).toUpperCase() || 'USD';

  // Data quality tier
  const tier = determineDataQualityTier(model_version, inputs);

  // OOD checks
  const oodStatus = checkIsOOD(inputs);

  // Drivers and assumptions
  const drivers = deriveEstimateDrivers(inputs, sizeValue);
  const assumptions = deriveEstimateAssumptions(inputs.hourly_rate_usd, cleanCurrency);

  // SHA256 model checksum
  const sha256 = '0bea59fbe69a5b17acdf9953d61e659b26d3450052fd8934b2b1e0b716e0b257';

  return {
    estimate_id: validUUID,
    project_name: project_name || 'PredictIQ Estimate',
    effort_hours: {
      p10: p10Hours,
      p50: p50Hours,
      p90: p90Hours,
    },
    person_months: {
      p10: p10PM,
      p50: p50PM,
      p90: p90PM,
    },
    cost: {
      p10: p10Cost,
      p50: p50Cost,
      p90: p90Cost,
      currency: cleanCurrency,
      rate: inputs.hourly_rate_usd || 75.0,
    },
    size: {
      value: sizeValue,
      source: sizeSource,
      uncertainty: {
        p10: Math.round(sizeValue * 0.85 * 10) / 10,
        p50: sizeValue,
        p90: Math.round(sizeValue * 1.15 * 10) / 10,
      },
    },
    drivers,
    assumptions,
    data_quality_tier: tier,
    ood_flags: oodStatus.reasons,
    model: {
      version: model_version || '2.0.0-rc.1',
      sha256,
      trained_on_rows: 915,
      sources: ['china', 'kitchenham', 'att', 'desharnais', 'maxwell', 'albrecht'],
      metrics_ref: 'docs/evidence/model_validation_summary.md',
    },
  };
}

/**
 * Validates whether a given object strictly adheres to docs/contracts/api_estimate_v2.json.
 */
export function validateV2Contract(payload: unknown): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!payload || typeof payload !== 'object') {
    return { isValid: false, errors: ['Payload must be a non-null object'] };
  }

  const p = payload as Record<string, unknown>;

  // Required top-level fields
  const requiredFields = [
    'estimate_id',
    'project_name',
    'effort_hours',
    'person_months',
    'cost',
    'size',
    'drivers',
    'assumptions',
    'data_quality_tier',
    'ood_flags',
    'model',
  ];

  for (const field of requiredFields) {
    if (p[field] === undefined || p[field] === null) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  // estimate_id format
  if (typeof p.estimate_id !== 'string' || !UUID_REGEX.test(p.estimate_id)) {
    errors.push(`Invalid UUID format for estimate_id: ${p.estimate_id}`);
  }

  // project_name minLength 1
  if (typeof p.project_name !== 'string' || p.project_name.length < 1) {
    errors.push('project_name must be a non-empty string');
  }

  // effort_hours
  if (p.effort_hours && typeof p.effort_hours === 'object') {
    const eh = p.effort_hours as Record<string, unknown>;
    for (const q of ['p10', 'p50', 'p90']) {
      if (typeof eh[q] !== 'number' || (eh[q] as number) < 0) {
        errors.push(`effort_hours.${q} must be a number >= 0`);
      }
    }
  }

  // person_months
  if (p.person_months && typeof p.person_months === 'object') {
    const pm = p.person_months as Record<string, unknown>;
    for (const q of ['p10', 'p50', 'p90']) {
      if (typeof pm[q] !== 'number' || (pm[q] as number) < 0) {
        errors.push(`person_months.${q} must be a number >= 0`);
      }
    }
  }

  // cost
  if (p.cost && typeof p.cost === 'object') {
    const c = p.cost as Record<string, unknown>;
    for (const q of ['p10', 'p50', 'p90', 'rate']) {
      if (typeof c[q] !== 'number' || (c[q] as number) < 0) {
        errors.push(`cost.${q} must be a number >= 0`);
      }
    }
    if (typeof c.currency !== 'string' || !/^[A-Z]{3}$/.test(c.currency)) {
      errors.push(`cost.currency must be a 3-letter uppercase code, got: ${c.currency}`);
    }
  }

  // size
  if (p.size && typeof p.size === 'object') {
    const s = p.size as Record<string, unknown>;
    if (typeof s.value !== 'number' || s.value < 0) {
      errors.push('size.value must be a number >= 0');
    }
    if (s.source !== 'user' && s.source !== 'nlp') {
      errors.push(`size.source must be 'user' or 'nlp', got: ${s.source}`);
    }
    if (s.uncertainty && typeof s.uncertainty === 'object') {
      const u = s.uncertainty as Record<string, unknown>;
      for (const q of ['p10', 'p50', 'p90']) {
        if (typeof u[q] !== 'number' || (u[q] as number) < 0) {
          errors.push(`size.uncertainty.${q} must be a number >= 0`);
        }
      }
    } else {
      errors.push('size.uncertainty is required');
    }
  }

  // data_quality_tier
  if (p.data_quality_tier !== 'A' && p.data_quality_tier !== 'B' && p.data_quality_tier !== 'C') {
    errors.push(`data_quality_tier must be 'A', 'B', or 'C', got: ${p.data_quality_tier}`);
  }

  // ood_flags
  if (!Array.isArray(p.ood_flags)) {
    errors.push('ood_flags must be an array of strings');
  }

  // model
  if (p.model && typeof p.model === 'object') {
    const m = p.model as Record<string, unknown>;
    if (typeof m.version !== 'string') errors.push('model.version must be a string');
    if (typeof m.sha256 !== 'string' || !SHA256_REGEX.test(m.sha256)) {
      errors.push('model.sha256 must be a 64-char hex string');
    }
    if (typeof m.trained_on_rows !== 'number' || m.trained_on_rows < 1) {
      errors.push('model.trained_on_rows must be integer >= 1');
    }
    if (!Array.isArray(m.sources)) errors.push('model.sources must be an array of strings');
    if (typeof m.metrics_ref !== 'string') errors.push('model.metrics_ref must be a string');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}
