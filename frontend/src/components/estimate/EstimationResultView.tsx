import React, { useState } from 'react';
import type { EstimateResult } from '@/types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/shared/Card';
import { Badge, DataQualityBadge, UncertaintyBadge, ModelVersionBadge } from '@/components/shared/Badge';
import { ConfidenceRangeBar, ConfidenceIntervalCard } from '@/components/shared/ConfidenceInterval';
import { Heading, Text, MetricValue, CodeChip } from '@/components/shared/Typography';
import {
  Download,
  FileDown,
  Share2,
  Copy,
  AlertTriangle,
  Clock,
  Shield,
  TrendingUp,
  Info,
  Layers,
  ArrowRight,
  CheckCircle,
  HelpCircle,
} from 'lucide-react';
import {
  hoursToPersonMonths,
  determineDataQualityTier,
  checkIsOOD,
  TIER_PROVENANCE,
} from './estimateUtils';
import { ModelTransparencyModal } from './ModelTransparencyModal';
import { OODDiagnosticsCard } from './OODDiagnosticsCard';
import { formatEstimateToV2Contract } from './exportContractUtils';
import { RISK_COLORS } from '@/lib/risk';

export interface EstimationResultViewProps {
  estimate: EstimateResult;
  onExportPDF?: () => void;
  onExportJSON?: () => void;
  onShare?: () => void;
  onDuplicate?: () => void;
  currencySymbol?: string;
  currencyRate?: number;
  currencyCode?: string;
  formatCurrency?: (val: number) => string;
  showExtendedBreakdown?: boolean;
  activeChartType?: 'bar' | 'polar' | 'pie' | 'line';
  onChartTypeChange?: (type: 'bar' | 'polar' | 'pie' | 'line') => void;
  renderChartContent?: () => React.ReactNode;
  className?: string;
}

export const EstimationResultView: React.FC<EstimationResultViewProps> = ({
  estimate,
  onExportPDF,
  onExportJSON,
  onShare,
  onDuplicate,
  currencySymbol = '$',
  currencyRate = 1,
  currencyCode = 'USD',
  formatCurrency,
  showExtendedBreakdown = true,
  activeChartType = 'bar',
  onChartTypeChange,
  renderChartContent,
  className = '',
}) => {
  const [showTierModal, setShowTierModal] = useState(false);
  const [showTransparencyModal, setShowTransparencyModal] = useState(false);
  const [copiedJSON, setCopiedJSON] = useState(false);
  const { inputs, outputs, model_version, project_name, estimate_id } = estimate;

  // Format currency helper
  const fmtMoney = (val: number): string => {
    if (formatCurrency) return formatCurrency(val);
    const converted = val * currencyRate;
    return `${currencySymbol}${Math.round(converted).toLocaleString('en-US')}`;
  };

  const handleCopyJSON = async () => {
    try {
      const contractPayload = formatEstimateToV2Contract(estimate, currencyCode, currencyRate);
      await navigator.clipboard.writeText(JSON.stringify(contractPayload, null, 2));
      setCopiedJSON(true);
      setTimeout(() => setCopiedJSON(false), 2500);
    } catch {
      // Fallback
    }
  };

  // Statistical calculations
  const tier = determineDataQualityTier(model_version, inputs);
  const tierInfo = TIER_PROVENANCE[tier];
  const oodStatus = checkIsOOD(inputs);
  const riskColor = RISK_COLORS[outputs.risk_level] || '#64748B';

  const p10Hours = outputs.effort_min_hours;
  const p50Hours = outputs.effort_likely_hours;
  const p90Hours = outputs.effort_max_hours;

  const p10PM = hoursToPersonMonths(p10Hours);
  const p50PM = hoursToPersonMonths(p50Hours);
  const p90PM = hoursToPersonMonths(p90Hours);

  const isCalibrated = model_version.startsWith('production-v3-') || tier !== 'C';

  return (
    <div className={`estimation-result-view space-y-6 ${className}`.trim()}>
      {/* ── Top Header & Metadata Badges ────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-[var(--shadow-card)]">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <button
              type="button"
              className="relative inline-flex items-center cursor-pointer border-0 bg-transparent p-0"
              onClick={() => setShowTransparencyModal(true)}
              title={`${tierInfo.name}: Click for model transparency & data provenance`}
              data-testid="tier-badge-transparency-trigger"
            >
              <DataQualityBadge tier={tier} showIcon />
            </button>
            <UncertaintyBadge
              calibrated={isCalibrated}
              interval="80% CI (p10–p90)"
              coverage={`${outputs.confidence_pct.toFixed(0)}% Conformal`}
            />
            <ModelVersionBadge version={model_version} />
          </div>
          <Heading level={2} className="text-xl sm:text-2xl font-bold text-[var(--text-primary)]">
            {project_name}
          </Heading>
          <Text variant="caption" className="text-xs text-[var(--text-tertiary)] mt-0.5">
            {inputs.project_type} • Version {estimate.version} • Created {new Date(estimate.created_at).toLocaleDateString()}
          </Text>
        </div>

        {/* Action Buttons Toolbar */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={() => setShowTransparencyModal(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/50 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 transition shadow-sm cursor-pointer"
            title="View full model provenance, empirical benchmarks, and calibration architecture"
            data-testid="how-it-works-button"
          >
            <HelpCircle size={14} className="text-blue-600 dark:text-blue-400" />
            <span>How this estimate works</span>
          </button>

          {onExportPDF && (
            <button
              type="button"
              onClick={onExportPDF}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[var(--bg-elevated)] hover:bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-color)] transition shadow-sm"
              title="Download PDF report with executive summary and breakdown"
            >
              <Download size={14} className="text-blue-600 dark:text-blue-400" />
              <span>PDF ({currencyCode})</span>
            </button>
          )}

          {onExportJSON && (
            <button
              type="button"
              onClick={onExportJSON}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[var(--bg-elevated)] hover:bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-color)] transition shadow-sm"
              title="Export complete calibrated predictions & metadata adhering to api_estimate_v2.json"
              data-testid="export-json-button"
            >
              <FileDown size={14} className="text-emerald-600 dark:text-emerald-400" />
              <span>Export JSON</span>
            </button>
          )}

          <button
            type="button"
            onClick={handleCopyJSON}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[var(--bg-elevated)] hover:bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-color)] transition shadow-sm cursor-pointer"
            title="Copy contract-compliant v2 JSON payload to clipboard"
            data-testid="copy-json-button"
          >
            {copiedJSON ? (
              <CheckCircle size={14} className="text-emerald-600 dark:text-emerald-400" />
            ) : (
              <Copy size={14} className="text-blue-600 dark:text-blue-400" />
            )}
            <span>{copiedJSON ? 'Copied JSON!' : 'Copy JSON'}</span>
          </button>

          {onShare && (
            <button
              type="button"
              onClick={onShare}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[var(--bg-elevated)] hover:bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-color)] transition shadow-sm"
              title="Generate a 7-day shareable read-only link"
            >
              <Share2 size={14} className="text-purple-600 dark:text-purple-400" />
              <span>Share</span>
            </button>
          )}

          {onDuplicate && (
            <button
              type="button"
              onClick={onDuplicate}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[var(--bg-elevated)] hover:bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-color)] transition shadow-sm"
              title="Duplicate estimate into a new scenario"
            >
              <Copy size={14} className="text-slate-600 dark:text-slate-400" />
              <span>Duplicate</span>
            </button>
          )}
        </div>
      </div>

      {/* ── Data Provenance Details Accordion / Tooltip Box ── */}
      {showTierModal && (
        <Card variant="subtle" padding="sm" className="border-blue-200 dark:border-blue-900 bg-blue-50/50 dark:bg-blue-950/20 text-xs animate-fade-in">
          <div className="flex items-start justify-between gap-2">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-bold text-blue-900 dark:text-blue-300">{tierInfo.name}</span>
                <Badge variant="primary" size="xs">{tierInfo.coverage}</Badge>
              </div>
              <p className="text-blue-800 dark:text-blue-200">{tierInfo.description}</p>
              <div className="flex items-center gap-1.5 pt-1 text-[11px] text-blue-700 dark:text-blue-300">
                <span className="font-semibold">Validated Sources:</span>
                {tierInfo.sources.map((s, idx) => (
                  <span key={idx} className="px-1.5 py-0.5 rounded bg-blue-100/70 dark:bg-blue-900/60 font-mono">
                    {s}
                  </span>
                ))}
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowTierModal(false)}
              className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 font-semibold"
            >
              Close
            </button>
          </div>
        </Card>
      )}

      {/* ── Out of Distribution (OOD) Guidance & Explanations ── */}
      <OODDiagnosticsCard inputs={inputs} reasons={oodStatus.reasons} />

      {/* ── Primary Confidence Interval Card (Effort Hours & PM) ── */}
      <Card variant="elevated" padding="md" className="border-t-4 border-t-[var(--color-primary)]">
        <CardHeader>
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <CardTitle as="h3" className="text-lg sm:text-xl flex items-center gap-2">
                <span>Calibrated Effort Ranges</span>
                <span className="text-xs font-normal text-[var(--text-secondary)]">
                  (Hours &amp; Person-Months at 152 hrs/PM)
                </span>
              </CardTitle>
              <CardDescription className="text-xs">
                Split-conformal prediction intervals with p10 (optimistic), p50 (calibrated median), and p90 (conservative ceiling)
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="primary" size="xs" pill>
                Standard Labor Unit: 152 hrs = 1 PM
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-2">
          {/* Visual Range Bar with median pip */}
          <ConfidenceRangeBar
            p10={p10Hours}
            p50={p50Hours}
            p90={p90Hours}
            unit="hours"
            formatValue={(val) => `${Math.round(val).toLocaleString('en-US')} hrs (${hoursToPersonMonths(val).formatted})`}
            showLabels
            showDetails
            ariaLabel="Calibrated effort range bar"
          />

          {/* Effort Summary 3-Column Quantiles Box */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4 pt-3 border-t border-[var(--border-subtle)] text-center">
            {/* p10 */}
            <div className="p-3 rounded-lg bg-[var(--bg-elevated)] border border-emerald-500/20">
              <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">
                p10 Lower Bound (Optimistic)
              </span>
              <span className="font-mono text-xl sm:text-2xl font-bold text-[var(--text-primary)] block mt-1">
                {Math.round(p10Hours).toLocaleString('en-US')} hrs
              </span>
              <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300 block">
                {p10PM.formatted} person-months
              </span>
              <span className="text-[11px] text-[var(--text-tertiary)] block mt-0.5">
                {fmtMoney(outputs.cost_min_usd)}
              </span>
            </div>

            {/* p50 */}
            <div className="p-3 rounded-lg bg-[var(--bg-elevated)] border-2 border-blue-600 dark:border-blue-500 shadow-sm relative">
              <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-600 text-white uppercase tracking-wider">
                Calibrated Center
              </span>
              <span className="text-[11px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider block mt-1">
                p50 Median (Most Likely)
              </span>
              <span className="font-mono text-2xl sm:text-3xl font-extrabold text-[var(--color-primary)] dark:text-blue-400 block mt-1">
                {Math.round(p50Hours).toLocaleString('en-US')} hrs
              </span>
              <span className="text-xs font-bold text-blue-700 dark:text-blue-300 block">
                {p50PM.formatted} person-months
              </span>
              <span className="text-xs font-bold text-[var(--text-primary)] block mt-0.5">
                {fmtMoney(outputs.cost_likely_usd)}
              </span>
            </div>

            {/* p90 */}
            <div className="p-3 rounded-lg bg-[var(--bg-elevated)] border border-amber-500/20">
              <span className="text-[11px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider block">
                p90 Upper Bound (Budget Cap)
              </span>
              <span className="font-mono text-xl sm:text-2xl font-bold text-[var(--text-primary)] block mt-1">
                {Math.round(p90Hours).toLocaleString('en-US')} hrs
              </span>
              <span className="text-xs font-semibold text-amber-700 dark:text-amber-300 block">
                {p90PM.formatted} person-months
              </span>
              <span className="text-[11px] text-[var(--text-tertiary)] block mt-0.5">
                {fmtMoney(outputs.cost_max_usd)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Cost, Confidence, Timeline, and Risk Summary ──── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Most Likely Cost */}
        <Card variant="default" padding="sm" className="text-center">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-tertiary)]">
            Most Likely Cost
          </span>
          <p className="font-mono text-2xl font-bold text-[var(--color-primary)] mt-1">
            {fmtMoney(outputs.cost_likely_usd)}
          </p>
          <span className="text-xs text-[var(--text-secondary)] mt-0.5 block">
            {fmtMoney(outputs.cost_min_usd)} – {fmtMoney(outputs.cost_max_usd)} range
          </span>
        </Card>

        {/* Timeline */}
        <Card variant="default" padding="sm" className="text-center">
          <div className="flex items-center justify-center gap-1 text-emerald-600 dark:text-emerald-400">
            <Clock size={16} />
            <span className="text-[11px] font-bold uppercase tracking-wider">
              Project Timeline
            </span>
          </div>
          <p className="font-mono text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
            {outputs.timeline_likely_weeks.toFixed(0)} wks
          </p>
          <span className="text-xs text-[var(--text-secondary)] mt-0.5 block">
            {outputs.timeline_min_weeks.toFixed(0)}–{outputs.timeline_max_weeks.toFixed(0)} wks range
          </span>
        </Card>

        {/* Validation Coverage / Confidence */}
        <Card variant="default" padding="sm" className="text-center">
          <div className="flex items-center justify-center gap-1 text-blue-600 dark:text-blue-400">
            <TrendingUp size={16} />
            <span className="text-[11px] font-bold uppercase tracking-wider">
              Interval Coverage
            </span>
          </div>
          <p className="font-mono text-2xl font-bold text-[var(--color-primary)] mt-1">
            {outputs.confidence_pct.toFixed(0)}%
          </p>
          <span className="text-xs text-[var(--text-secondary)] mt-0.5 block">
            {isCalibrated ? 'Validation interval coverage' : 'Heuristic confidence'}
          </span>
        </Card>

        {/* Risk Score */}
        <Card variant="default" padding="sm" className="text-center">
          <div className="flex items-center justify-center gap-1" style={{ color: riskColor }}>
            <Shield size={16} />
            <span className="text-[11px] font-bold uppercase tracking-wider">
              Risk Profile
            </span>
          </div>
          <p className="font-mono text-2xl font-bold mt-1" style={{ color: riskColor }}>
            {outputs.risk_score.toFixed(0)}/100
          </p>
          <span className="text-xs font-semibold mt-0.5 block">
            <span className={`risk-badge risk-${outputs.risk_level.toLowerCase()}`}>
              {outputs.risk_level} Risk
            </span>
          </span>
        </Card>
      </div>

      {/* ── Extended Breakdown (Charts & Phases) ──────────── */}
      {showExtendedBreakdown && renderChartContent && (
        <Card variant="default" padding="md">
          <CardHeader>
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <CardTitle as="h3" className="text-base sm:text-lg flex items-center gap-2">
                <TrendingUp size={18} className="text-blue-600 dark:text-blue-400" />
                <span>Phase Breakdown &amp; Resource Distribution</span>
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="mt-2">
            <div style={{ height: 280 }}>{renderChartContent()}</div>
          </CardContent>
        </Card>
      )}

      {/* ── Input Parameters Audit Card ───────────────────── */}
      <Card variant="subtle" padding="md">
        <CardHeader>
          <CardTitle as="h3" className="text-sm sm:text-base font-semibold flex items-center gap-2">
            <Layers size={16} className="text-[var(--text-secondary)]" />
            <span>Input Parameters</span>
          </CardTitle>
          <CardDescription className="text-xs">
            Persisted inputs and functional sizing parameters for auditability
          </CardDescription>
        </CardHeader>
        <CardContent className="mt-2">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 text-xs">
            {[
              { label: 'Project Type', value: inputs.project_type },
              { label: 'Team Size', value: inputs.team_size?.toString() },
              { label: 'Duration', value: `${inputs.duration_months} months` },
              { label: 'Complexity', value: inputs.complexity },
              { label: 'Methodology', value: inputs.methodology },
              { label: 'Hourly Rate', value: `$${inputs.hourly_rate_usd}/hr` },
              { label: 'Tech Stack', value: inputs.tech_stack?.join(', ') || 'Not specified' },
              { label: 'Features', value: inputs.feature_count ?? 'Not recorded' },
              { label: 'Integrations', value: inputs.integration_count ?? 'Not recorded' },
              { label: 'Requirements Volatility (1–5)', value: inputs.volatility_score ?? 'Not recorded' },
              { label: 'Team Experience (1–4)', value: inputs.team_experience ?? 'Not recorded' },
              { label: 'Function Points', value: inputs.size_fp ?? 'Not recorded' },
            ].map((item, i) => (
              <div key={i} className="p-2 rounded bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
                <span className="text-[10px] uppercase font-bold text-[var(--text-tertiary)] block tracking-wider">
                  {item.label}
                </span>
                <span className="font-semibold text-[var(--text-primary)] text-xs mt-0.5 block truncate">
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ── Model Transparency & Data Provenance Modal ────── */}
      <ModelTransparencyModal
        isOpen={showTransparencyModal}
        onClose={() => setShowTransparencyModal(false)}
        modelVersion={model_version}
        tier={tier}
        sizeFp={inputs.size_fp}
        estimate={estimate}
        currencyCode={currencyCode}
        currencyRate={currencyRate}
      />
    </div>
  );
};

export default EstimationResultView;
