export interface EstimateInputs {
  project_type: string;
  tech_stack: string[];
  team_size: number;
  duration_months: number;
  complexity: string;
  methodology: string;
  hourly_rate_usd: number;
}

export interface RiskItem {
  name: string;
  description: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface PhaseBreakdown {
  phase: string;
  effort_hours: number;
  cost_usd: number;
  duration_weeks: number;
  pct_of_total: number;
}

export interface EstimateOutputs {
  effort_min_hours: number;
  effort_likely_hours: number;
  effort_max_hours: number;
  cost_min_usd: number;
  cost_likely_usd: number;
  cost_max_usd: number;
  timeline_min_weeks: number;
  timeline_likely_weeks: number;
  timeline_max_weeks: number;
  confidence_pct: number;
  risk_score: number;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  top_risks: RiskItem[];
  phase_breakdown: PhaseBreakdown[];
  model_explanation: string;
  benchmark_comparison: string;
}

export interface EstimateResult {
  estimate_id: string;
  document_id: string | null;
  user_id: string;
  project_name: string;
  created_at: string;
  version: number;
  status: string;
  inputs: EstimateInputs;
  outputs: EstimateOutputs;
  model_version: string;
}

export interface EstimateSummary {
  id: string;
  project_name: string;
  project_type: string;
  cost_likely_usd: number;
  cost_min_usd: number;
  cost_max_usd: number;
  risk_score: number;
  risk_level: string;
  confidence_pct: number;
  duration_likely_weeks: number;
  status: string;
  version: number;
  created_at: string;
  updated_at?: string;
}

export interface UserProfile {
  id: string;
  full_name: string | null;
  avatar_url: string | null;
  hourly_rate_usd: number;
  currency: string;
  theme: string;
  timezone: string;
}
