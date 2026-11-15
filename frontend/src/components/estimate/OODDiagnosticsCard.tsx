import React, { useState } from 'react';
import type { EstimateInputs } from '@/types';
import { Card } from '@/components/shared/Card';
import { Badge } from '@/components/shared/Badge';
import { AlertTriangle, ChevronDown, ChevronUp, Layers, CheckCircle2 } from 'lucide-react';
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
                Large project notice
              </span>
              <Badge variant="warning" size="xs" pill>
                Wider range
              </Badge>
            </div>
            <p className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">
              One or more inputs are larger than most projects in our data, so the estimate range is wider.
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
          <span>{isExpanded ? 'Hide details' : 'View details'}</span>
          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* ── Expandable Details Panel ───────────────────────── */}
      {isExpanded && (
        <div
          className="px-4 pb-4 pt-2 border-t border-amber-200/60 dark:border-amber-900/60 space-y-4 animate-fade-in text-xs"
          data-testid="ood-expanded-panel"
        >
          {/* Section 1: Detected Parameters */}
          <div>
            <h4 className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5 mb-1.5">
              <Layers size={14} className="text-amber-600 dark:text-amber-400" />
              <span>Project scope factors</span>
            </h4>
            <ul className="list-disc list-inside space-y-1 text-amber-800 dark:text-amber-300 pl-1">
              {reasons.map((reason, idx) => (
                <li key={idx} className="leading-relaxed">
                  <span className="font-medium">{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Section 2: Recommendations */}
          <div>
            <h4 className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5 mb-1.5">
              <CheckCircle2 size={14} className="text-emerald-600 dark:text-emerald-400" />
              <span>Suggestions</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] text-amber-900 dark:text-amber-200">
              <div className="p-2 rounded bg-white/60 dark:bg-slate-900/40 border border-amber-200 dark:border-amber-900/60">
                <span className="font-bold block text-amber-950 dark:text-amber-100">Scope phasing</span>
                Break large deliverables into iterative releases or milestones.
              </div>
              <div className="p-2 rounded bg-white/60 dark:bg-slate-900/40 border border-amber-200 dark:border-amber-900/60">
                <span className="font-bold block text-amber-950 dark:text-amber-100">Team squads</span>
                Organize large teams into smaller, focused delivery squads.
              </div>
              <div className="p-2 rounded bg-white/60 dark:bg-slate-900/40 border border-amber-200 dark:border-amber-900/60">
                <span className="font-bold block text-amber-950 dark:text-amber-100">Iterative schedule</span>
                Plan long timelines in quarterly increments.
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

export default OODDiagnosticsCard;
