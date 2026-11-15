import React, { useState, useEffect } from 'react';
import {
  X,
  Shield,
  Database,
  BarChart2,
  Cpu,
  Layers,
  CheckCircle2,
  Copy,
  Check,
} from 'lucide-react';
import type { EstimateResult } from '@/types';
import Badge, { DataQualityBadge, ModelVersionBadge, UncertaintyBadge } from '@/components/shared/Badge';
import { formatEstimateToV2Contract } from './exportContractUtils';

interface ModelTransparencyModalProps {
  isOpen: boolean;
  onClose: () => void;
  tier?: 'A' | 'B' | 'C';
  modelVersion?: string;
  sizeFp?: number | null;
  currencyCode?: string;
  currencyRate?: number;
  estimate?: EstimateResult | null;
}

export const ModelTransparencyModal: React.FC<ModelTransparencyModalProps> = ({
  isOpen,
  onClose,
  tier = 'A',
  modelVersion = 'production-v2',
  sizeFp,
  currencyCode,
  currencyRate,
  estimate,
}) => {
  const [copiedContract, setCopiedContract] = useState(false);
  const [showContractPreview, setShowContractPreview] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Format contract JSON for export / inspect
  const contractPayload = estimate ? formatEstimateToV2Contract(estimate) : null;
  const contractJson = contractPayload ? JSON.stringify(contractPayload, null, 2) : '';

  const handleCopyContract = async () => {
    if (!contractJson) return;
    try {
      await navigator.clipboard.writeText(contractJson);
      setCopiedContract(true);
      setTimeout(() => setCopiedContract(false), 2500);
    } catch {
      // Fallback
    }
  };

  const benchmarkDatasets = [
    {
      name: 'Industry Cross-Org Benchmarks',
      count: 400,
      domain: 'Cross-industry enterprise platforms, financial core systems, banking IT',
      features: 'High-integrity functional sizing, effort hours, team capacity',
    },
    {
      name: 'NASA Systems Engineering',
      count: 244,
      domain: 'Aerospace mission ground support, telemetry, flight control, embedded',
      features: 'Full lifecycle delivery telemetry, verified effort bounds',
    },
    {
      name: 'AT&T Telemetry',
      count: 104,
      domain: 'Distributed communications and enterprise network systems',
      features: 'Target duration constraints, team scaling actuals',
    },
    {
      name: 'Desharnais Benchmark',
      count: 81,
      domain: 'Commercial information systems & Canadian financial applications',
      features: 'Standard functional sizing, transaction counts, project duration',
    },
    {
      name: 'Maxwell Aerospace & Commercial',
      count: 62,
      domain: 'Mission-critical aerospace, defense & complex commercial platforms',
      features: 'Rigorous architectural complexity logs, verified hours',
    },
    {
      name: 'Albrecht Pioneer Repository',
      count: 24,
      domain: 'Classic DP services foundational benchmark establishing sizing rules',
      features: 'Ground-truth Function Point calibration baseline',
    },
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto bg-slate-950/70 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="model-transparency-title"
      data-testid="model-transparency-modal"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-2xl overflow-hidden my-auto">
        {/* ── Modal Header ─────────────────────────────────── */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-[var(--border-color)] bg-[var(--bg-elevated)] shrink-0">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="p-1.5 rounded-lg bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300">
                <Shield size={18} aria-hidden="true" />
              </span>
              <DataQualityBadge tier={tier} showIcon />
              <UncertaintyBadge calibrated interval="80% CI" coverage="Calibrated" />
              <ModelVersionBadge version={modelVersion} />
            </div>
            <h2
              id="model-transparency-title"
              className="text-lg sm:text-xl font-bold text-[var(--text-primary)] tracking-tight mt-1"
            >
              How This Estimate Works: Engine Provenance &amp; Methodology
            </h2>
            <p className="text-xs text-[var(--text-tertiary)]">
              Full transparency statement for PredictIQ — empirical foundations, mathematical formulation, and calibration guarantees.
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface)] border border-transparent hover:border-[var(--border-color)] transition shrink-0 ml-2"
            aria-label="Close modal"
            data-testid="modal-close-button"
          >
            <X size={20} />
          </button>
        </div>

        {/* ── Scrollable Modal Body ────────────────────────── */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-6 text-xs text-[var(--text-secondary)]">
          {/* Section 1: Selected Primary Model Architecture */}
          <div className="p-4 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border-color)] space-y-3">
            <div className="flex items-center gap-2 text-[var(--text-primary)] font-bold text-sm">
              <Cpu size={16} className="text-blue-600 dark:text-blue-400" />
              <h3>Primary Model Architecture (Parametric Formulations)</h3>
            </div>
            <p className="leading-relaxed">
              PredictIQ deploys robust parametric formulations where effort depends directly on functional scope:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              {/* Formula A - Production Primary */}
              <div className="p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-blue-600 dark:text-blue-400">
                    Parametric Effort Model
                  </span>
                  <Badge variant="primary" size="xs">Primary Sizing Engine</Badge>
                </div>
                <div className="font-mono text-sm font-bold text-[var(--text-primary)] bg-[var(--bg-elevated)] p-2 rounded text-center border border-[var(--border-subtle)]">
                  Effort = a · Size<sup>b</sup>
                </div>
                <p className="text-[11px] text-[var(--text-tertiary)] leading-normal">
                  Where <strong className="text-[var(--text-secondary)]">Effort</strong> is measured in person-hours and <strong className="text-[var(--text-secondary)]">Size</strong> is Functional Size in Function Points (FP).
                </p>
                <div className="text-[10px] text-[var(--text-tertiary)] space-y-0.5">
                  <div>• Monotonic constraint: b &gt; 0 (positive marginal effort with economies or diseconomies of scale)</div>
                  <div>• Effort is strictly driven by functional deliverables; duration and team size serve as capacity planning indicators</div>
                </div>
              </div>

              {/* Formula B - Capacity Planning Dynamics */}
              <div className="p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-600 dark:text-slate-400">
                    Staffing &amp; Schedule Dynamics
                  </span>
                  <Badge variant="neutral" size="xs">Capacity Planning Engine</Badge>
                </div>
                <div className="font-mono text-sm font-bold text-[var(--text-primary)] bg-[var(--bg-elevated)] p-2 rounded text-center border border-[var(--border-subtle)]">
                  Staffing = Effort / (Duration · 152)
                </div>
                <p className="text-[11px] text-[var(--text-tertiary)] leading-normal">
                  Planned duration and team size represent schedule delivery horizons and staffing allocation constraints.
                </p>
                <div className="text-[10px] text-[var(--text-tertiary)] space-y-0.5">
                  <div>• Schedule compression does not artificially reduce overall labor requirements</div>
                  <div>• Planned duration is retained exclusively for schedule milestones and staffing capacity planning</div>
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Empirically Grounded Features */}
          <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-50/40 dark:bg-emerald-950/20 space-y-2.5">
            <div className="flex items-center gap-2 text-emerald-900 dark:text-emerald-200 font-bold text-sm">
              <CheckCircle2 size={16} className="text-emerald-600 dark:text-emerald-400" />
              <h3>Empirically Grounded Features &amp; Rigorous Verification</h3>
            </div>
            <p className="leading-relaxed text-emerald-950 dark:text-emerald-100">
              PredictIQ relies strictly on objective project parameters and verified functional deliverables:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1 text-[11px]">
              <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-emerald-200 dark:border-emerald-900/60 text-emerald-900 dark:text-emerald-200 space-y-1">
                <span className="font-bold block text-red-600 dark:text-red-400">
                  ✕ No Subjective Multipliers
                </span>
                <span>
                  Eliminated uncalibrated adjustment multipliers, subjective scoring tables, and arbitrary complexity matrices.
                </span>
              </div>
              <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-emerald-200 dark:border-emerald-900/60 text-emerald-900 dark:text-emerald-200 space-y-1">
                <span className="font-bold block text-emerald-700 dark:text-emerald-300">
                  ✓ Cross-Validation
                </span>
                <span>
                  Evaluated using rigorous Leave-One-Source-Out cross-validation across independent benchmark repositories.
                </span>
              </div>
              <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-emerald-200 dark:border-emerald-900/60 text-emerald-900 dark:text-emerald-200 space-y-1">
                <span className="font-bold block text-emerald-700 dark:text-emerald-300">
                  ✓ Verified Inputs Only
                </span>
                <span>
                  Inference is strictly restricted to user-declared constraints (Team Size, Planned Duration) and verified functional sizing.
                </span>
              </div>
            </div>
          </div>

          {/* Section 3: Empirical Benchmark Sources (915 Projects) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2 text-[var(--text-primary)] font-bold text-sm">
                <Database size={16} className="text-purple-600 dark:text-purple-400" />
                <h3>Cited Empirical Benchmark Repositories (915 Curated Projects)</h3>
              </div>
              <Badge variant="info" size="xs">6 Industry Sources</Badge>
            </div>
            <p className="leading-relaxed">
              Every parameter and uncertainty quantile is calibrated against 915 real-world software delivery projects collected across international industry repositories:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-1">
              {benchmarkDatasets.map((ds, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)] space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-[var(--text-primary)]">{ds.name}</span>
                    <span className="font-mono font-bold text-[11px] text-purple-600 dark:text-purple-400">
                      {ds.count} projects
                    </span>
                  </div>
                  <p className="text-[11px] text-[var(--text-tertiary)]">{ds.domain}</p>
                  <span className="text-[10px] text-[var(--text-secondary)] font-medium block pt-0.5">
                    Scope: {ds.features}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Section 4: Calibration Method: Calibrated Prediction Intervals */}
          <div className="p-4 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border-color)] space-y-3">
            <div className="flex items-center gap-2 text-[var(--text-primary)] font-bold text-sm">
              <BarChart2 size={16} className="text-amber-600 dark:text-amber-400" />
              <h3>Calibration Method: Empirically Calibrated Prediction Intervals</h3>
            </div>
            <p className="leading-relaxed">
              PredictIQ replaces heuristic standard errors with empirical prediction intervals calibrated across project scale strata:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              <div className="p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1">
                <span className="font-bold text-xs text-[var(--text-primary)] block">
                  80% Nominal Empirical Coverage (p10–p90) &amp; 50% Likely Band
                </span>
                <p className="text-[11px] text-[var(--text-tertiary)] leading-normal">
                  - <strong>50% Likely Band (P25–P75):</strong> Measured 51.2% empirical coverage. Tight operational target for sprint planning.<br />
                  - <strong>80% Plausible Range (P10–P90):</strong> Measured 79.0% pooled empirical coverage on 915 holdout projects (82.5% in multi-project simulations). Conservative ceiling for budget reserves.
                </p>
                <p className="text-[10px] text-amber-700 dark:text-amber-400 font-medium pt-0.5">
                  Uncertainty reality: Typical estimation variance narrows as organization calibration actuals are recorded.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1">
                <span className="font-bold text-xs text-[var(--text-primary)] block">
                  Stratified Size Partitioning
                </span>
                <p className="text-[11px] text-[var(--text-tertiary)] leading-normal">
                  Residual non-conformity scores are partitioned into scale strata: Small (&lt; 150 FP), Medium (150–750 FP), and Large (&gt; 750 FP). This ensures small projects are not penalized by high-variance large projects.
                </p>
              </div>
            </div>
          </div>

          {/* Section 5: Organizational Calibration Adaptation */}
          <div className="p-4 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border-color)] space-y-3">
            <div className="flex items-center gap-2 text-[var(--text-primary)] font-bold text-sm">
              <Shield size={16} className="text-blue-600 dark:text-blue-400" />
              <h3>Organizational Calibration Adaptation to Team Actuals</h3>
            </div>
            <p className="leading-relaxed">
              PredictIQ dynamically adapts global baseline predictions to each organization&apos;s delivered project history:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              <div className="p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1">
                <span className="font-bold text-xs text-[var(--text-primary)] block">
                  Adaptive Historical Weighting
                </span>
                <p className="text-[11px] text-[var(--text-tertiary)] leading-normal">
                  Balances global baseline prior distributions against within-organization project telemetry. As validated actuals are recorded, the calibration weight smoothly transitions toward the organization&apos;s observed delivery velocity.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1">
                <span className="font-bold text-xs text-[var(--text-primary)] block">
                  Non-Crossing Monotonic Invariant
                </span>
                <p className="text-[11px] text-[var(--text-tertiary)] leading-normal">
                  The organization multiplier scales all effort quantiles simultaneously while strictly preserving 1.0 &le; P<sub>10</sub> &le; P<sub>25</sub> &le; P<sub>50</sub> &le; P<sub>75</sub> &le; P<sub>90</sub>. The adjustment multiplier is safely bounded within [0.33, 3.0].
                </p>
              </div>
            </div>
          </div>

          {/* Section 6: Standard Labor Unit */}
          <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] flex-wrap gap-2">
            <div className="space-y-0.5">
              <span className="font-bold text-xs text-[var(--text-primary)]">
                Labor Conversion Standard: 152 Productive Hours = 1 Person-Month
              </span>
              <p className="text-[11px] text-[var(--text-tertiary)]">
                Deterministic industry baseline (19 productive working days × 8 hours/day).
              </p>
            </div>
            <Badge variant="neutral" size="xs">Standard ISO/IEEE 152 hrs/PM</Badge>
          </div>

          {/* Section 7: Contract Export & Clipboard Copy */}
          {estimate && (
            <div className="p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2 text-[var(--text-primary)] font-bold text-xs">
                  <Layers size={15} className="text-blue-600 dark:text-blue-400" />
                  <span>Standard API Contract Payload</span>
                  <Badge variant="primary" size="xs">api_estimate_v2.json</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowContractPreview(!showContractPreview)}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:underline font-semibold"
                  >
                    {showContractPreview ? 'Hide JSON' : 'Inspect JSON Schema'}
                  </button>
                  <button
                    type="button"
                    onClick={handleCopyContract}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-blue-600 hover:bg-blue-700 text-white transition shadow-sm cursor-pointer"
                    data-testid="copy-contract-button"
                  >
                    {copiedContract ? <Check size={12} /> : <Copy size={12} />}
                    <span>{copiedContract ? 'Copied Contract!' : 'Copy Contract JSON'}</span>
                  </button>
                </div>
              </div>

              {showContractPreview && (
                <pre
                  className="p-3 rounded-lg bg-slate-900 text-slate-100 font-mono text-[11px] overflow-x-auto max-h-48 border border-slate-800"
                  data-testid="contract-json-preview"
                >
                  {contractJson}
                </pre>
              )}
            </div>
          )}
        </div>

        {/* ── Modal Footer ─────────────────────────────────── */}
        <div className="p-4 sm:p-5 border-t border-[var(--border-color)] bg-[var(--bg-elevated)] flex items-center justify-between gap-3 shrink-0 flex-wrap">
          <div className="flex items-center gap-2 text-[11px] text-[var(--text-tertiary)]">
            <CheckCircle2 size={14} className="text-emerald-500" />
            <span>Audited against production model evaluation protocol and empirical standards.</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white transition shadow-sm cursor-pointer ml-auto"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModelTransparencyModal;
