import React, { useState } from 'react';
import type { EstimateInputs } from '@/types';
import { Card } from '@/components/shared/Card';
import { Badge } from '@/components/shared/Badge';
import { AlertTriangle, ChevronDown, ChevronUp, Layers, HelpCircle, CheckCircle2 } from 'lucide-react';
import { checkIsOOD } from './estimateUtils';

export interface OODDiagnosticsCardProps {
  inputs?: Partial<EstimateInputs>;
  reasons?: string[];
  className?: string;
  defaultExpanded?: boolean;
}

export const OODDiagnosticsCard: React.FC<OODDiagnosticsCardProps> = ({
  inputs,
  reasons: initialReasons,
  className = '',
  defaultExpanded = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // If reasons are not provided, evaluate them from inputs
  const reasons = initialReasons && initialReasons.length > 0
    ? initialReasons
    : (inputs ? checkIsOOD(inputs).reasons : []);

  if (reasons.length === 0) {
    return null;
  }

  return (
    <Card
      variant="elevated"
      padding="none"
      className={`ood-diagnostics-card overflow-hidden border-l-4 border-l-amber-500 bg-amber-50/70 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900 transition-all ${className}`.trim()}
      data-testid="ood-diagnostics-card"
    >
      {/* ── Summary Header (Always Visible) ────────────────── */}
      <div className="p-4 flex items-start justify-between gap-3 flex-wrap sm:flex-nowrap">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/70 text-amber-700 dark:text-amber-300 shrink-0 mt-0.5">
            <AlertTriangle size={20} aria-hidden="true" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-sm text-amber-900 dark:text-amber-200">
                Out-of-Distribution (OOD) Parameter Notice
              </span>
              <Badge variant="warning" size="xs" pill>
                Statistical Variance Widened
              </Badge>
            </div>
            <p className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">
              One or more project parameters exceed empirical benchmark calibration envelopes. Prediction intervals carry wider variance without false clamping.
            </p>
          </div>
        </div>

        {/* Toggle Button */}
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-100 hover:bg-amber-200 dark:bg-amber-900/50 dark:hover:bg-amber-900/80 text-amber-900 dark:text-amber-200 border border-amber-300 dark:border-amber-800 transition shrink-0 self-start sm:self-center cursor-pointer"
          data-testid="ood-toggle-button"
        >
          <span>{isExpanded ? 'Hide Diagnostics' : 'View Diagnostics & Why Intervals Widen'}</span>
          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* ── Expandable Details Panel ───────────────────────── */}
      {isExpanded && (
        <div
          className="px-4 pb-4 pt-2 border-t border-amber-200/60 dark:border-amber-900/60 space-y-4 animate-fade-in text-xs"
          data-testid="ood-expanded-panel"
        >
          {/* Section 1: Detected Parameter Violations */}
          <div>
            <h4 className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5 mb-1.5">
              <Layers size={14} className="text-amber-600 dark:text-amber-400" />
              <span>Triggered Parameter Envelope Exceedances</span>
            </h4>
            <ul className="list-disc list-inside space-y-1 text-amber-800 dark:text-amber-300 pl-1">
              {reasons.map((reason, idx) => (
                <li key={idx} className="leading-relaxed">
                  <span className="font-medium">{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Section 2: Mathematical Rationale — Why Intervals Widen Without False Clamping */}
          <div className="p-3 rounded-lg bg-amber-100/60 dark:bg-amber-900/40 border border-amber-300/50 dark:border-amber-800/50 space-y-2">
            <h4 className="font-semibold text-amber-950 dark:text-amber-100 flex items-center gap-1.5">
              <HelpCircle size={14} className="text-amber-700 dark:text-amber-300" />
              <span>Statistical Mechanics: Why Intervals Widen Without Arbitrary Clamping</span>
            </h4>
            <p className="text-amber-900 dark:text-amber-200 leading-relaxed">
              Unlike legacy heuristic calculators that arbitrarily clamp predictions or project false certainty, PredictIQ v2 adheres to formal mathematical principles:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-1 text-[11px]">
              <div className="p-2 rounded bg-amber-50/80 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800/60">
                <span className="font-bold text-amber-950 dark:text-amber-200 block mb-0.5">
                  1. Conformal Residual Dispersion
                </span>
                <span className="text-amber-800 dark:text-amber-300">
                  Under split-conformal calibration with Mondrian size bucketing, residual variance grows with extrapolation distance. The p10–p90 band expands to preserve honest 80% empirical coverage.
                </span>
              </div>
              <div className="p-2 rounded bg-amber-50/80 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800/60">
                <span className="font-bold text-amber-950 dark:text-amber-200 block mb-0.5">
                  2. Monotonic Power-Law Scaling
                </span>
                <span className="text-amber-800 dark:text-amber-300">
                  The calibrated center (p50) preserves monotonic power-law dynamics (E = a · S<sup>b</sup> · D<sup>c</sup>) without sudden cliffs or artificial ceiling cutoffs, maintaining economic consistency.
                </span>
              </div>
            </div>
          </div>

          {/* Section 3: Recommended Risk Mitigations */}
          <div>
            <h4 className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5 mb-1.5">
              <CheckCircle2 size={14} className="text-emerald-600 dark:text-emerald-400" />
              <span>Recommended Engineering Mitigations</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] text-amber-900 dark:text-amber-200">
              <div className="p-2 rounded bg-white/60 dark:bg-slate-900/40 border border-amber-200 dark:border-amber-900/60">
                <span className="font-bold block text-amber-950 dark:text-amber-100">Scope Decomposition</span>
                Decompose large systems (&gt; 2,000 FP) into independent microservices or iterative milestone releases.
              </div>
              <div className="p-2 rounded bg-white/60 dark:bg-slate-900/40 border border-amber-200 dark:border-amber-900/60">
                <span className="font-bold block text-amber-950 dark:text-amber-100">Team Decoupling</span>
                Structure large teams (&gt; 30 members) into autonomous two-pizza pods with bounded context APIs.
              </div>
              <div className="p-2 rounded bg-white/60 dark:bg-slate-900/40 border border-amber-200 dark:border-amber-900/60">
                <span className="font-bold block text-amber-950 dark:text-amber-100">Horizon Phasing</span>
                Segment multi-year schedules (&gt; 24 mo) into quarterly deliverables to re-calibrate with empirical velocity.
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

export default OODDiagnosticsCard;
