import React, { useState } from 'react';
import type { EstimateResult } from '@/types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { Badge, DataQualityBadge } from '@/components/shared/Badge';
import { ConfidenceRangeBar } from '@/components/shared/ConfidenceInterval';
import { Heading, Text } from '@/components/shared/Typography';
import {
  Download,
  FileDown,
  Share2,
  Copy,
  Clock,
  Shield,
  TrendingUp,
  Layers,
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
  activeChartType: _activeChartType = 'bar',
  onChartTypeChange: _onChartTypeChange,
  renderChartContent,
  className = '',
}) => {
  const [showTransparencyModal, setShowTransparencyModal] = useState(false);
  const [copiedJSON, setCopiedJSON] = useState(false);
  const [showMoreActions, setShowMoreActions] = useState(false);
  const { inputs, outputs, model_version, project_name } = estimate;

  const hourlyRateConverted = Math.round((inputs.hourly_rate_usd || 75) * currencyRate);
  const rateLabel = `at ${currencySymbol}${hourlyRateConverted.toLocaleString('en-US')}/hour`;

  // Format currency helper with USD tooltip value
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
  const p25Hours = outputs.effort_p25_hours ?? outputs.effort_hours?.p25;
  const p75Hours = outputs.effort_p75_hours ?? outputs.effort_hours?.p75;

  const p10PM = hoursToPersonMonths(p10Hours);
  const p50PM = hoursToPersonMonths(p50Hours);
  const p90PM = hoursToPersonMonths(p90Hours);

  const displayFp = estimate.size?.value ?? inputs.size_fp ?? 'Not recorded';

  return (
    <div className={`estimation-result-view space-y-6 ${className}`.trim()}>
      {/* ── Top Header & Metadata Badges ────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-5 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-[var(--shadow-card)]">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1.5">
            {tier === 'B' ? (
              <Badge
                variant="neutral"
                size="sm"
                pill
                className="cursor-pointer font-medium"
                onClick={() => setShowTransparencyModal(true)}
                title="Size taken from your document - please review"
                data-testid="tier-badge-transparency-trigger"
              >
                Size from your document - please review
              </Badge>
            ) : (
              <button
                type="button"
                className="relative inline-flex items-center cursor-pointer border-0 bg-transparent p-0"
                onClick={() => setShowTransparencyModal(true)}
                title={`${tierInfo.name}: Click for estimate details`}
                data-testid="tier-badge-transparency-trigger"
              >
                <DataQualityBadge tier={tier} showIcon />
              </button>
            )}
          </div>
          <Heading level={2} className="text-xl sm:text-2xl font-bold text-[var(--text-primary)]">
            {project_name}
          </Heading>
          <Text variant="caption" className="text-xs text-[var(--text-tertiary)] mt-0.5">
            {inputs.project_type} • Version {estimate.version} • Created {new Date(estimate.created_at).toLocaleDateString()}
          </Text>
        </div>

        {/* Action Buttons Toolbar */}
        <div className="flex items-center gap-2 flex-wrap relative">
          <button
            type="button"
            onClick={() => setShowTransparencyModal(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/50 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 transition shadow-sm cursor-pointer"
            title="View details about this estimate"
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
              title="Download PDF report"
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
              title="Export estimate as JSON"
              data-testid="export-json-button"
            >
              <FileDown size={14} className="text-emerald-600 dark:text-emerald-400" />
              <span>Export JSON</span>
            </button>
          )}

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

          {/* More options menu hiding Copy JSON */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowMoreActions((prev) => !prev)}
              className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-xs font-semibold bg-[var(--bg-elevated)] hover:bg-[var(--bg-surface)] text-[var(--text-secondary)] border border-[var(--border-color)] transition shadow-sm"
              title="More actions"
              aria-label="More actions"
            >
              &bull;&bull;&bull;
            </button>
            {showMoreActions && (
              <div
                className="absolute right-0 mt-1 w-44 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-lg py-1 z-20"
                onMouseLeave={() => setShowMoreActions(false)}
              >
                <button
                  type="button"
                  onClick={() => {
                    handleCopyJSON();
                    setShowMoreActions(false);
                  }}
                  className="w-full text-left px-3 py-2 text-xs font-medium text-[var(--text-primary)] hover:bg-[var(--bg-elevated)] flex items-center gap-2"
                  data-testid="copy-json-button"
                >
                  {copiedJSON ? (
                    <CheckCircle size={14} className="text-emerald-600 dark:text-emerald-400" />
                  ) : (
                    <Copy size={14} className="text-blue-600 dark:text-blue-400" />
                  )}
                  <span>{copiedJSON ? 'Copied JSON!' : 'Copy JSON'}</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Out of Distribution (OOD) Guidance & Explanations ── */}
      <OODDiagnosticsCard inputs={inputs} reasons={oodStatus.reasons} />

      {/* ── Hero Card: Likely Effort, Person-Months & Cost ── */}
      <Card variant="elevated" padding="lg" className="border-t-4 border-t-blue-600 dark:border-t-blue-500 shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <CardTitle as="h3" className="text-lg sm:text-xl font-bold flex items-center gap-2">
                <span>Likely effort</span>
              </CardTitle>
              <CardDescription className="text-sm text-[var(--text-secondary)]">
                Most likely delivery effort based on your functional scope
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-2">
          {/* Hero 3-Column Effort & Cost Breakdown */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
            {/* p10 */}
            <div className="p-4 rounded-xl bg-[var(--bg-elevated)] border border-emerald-500/20">
              <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">
                Optimistic (P10)
              </span>
              <span className="font-mono text-xl sm:text-2xl font-bold text-[var(--text-primary)] block mt-1">
                {Math.round(p10Hours).toLocaleString('en-US')} hrs
              </span>
              <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300 block mt-0.5">
                {p10PM.formatted}
              </span>
              <span
                className="text-xs text-[var(--text-secondary)] block mt-1 cursor-help"
                title={`$${Math.round(outputs.cost_min_usd).toLocaleString('en-US')} USD`}
              >
                {fmtMoney(outputs.cost_min_usd)}
              </span>
            </div>

            {/* p50 */}
            <div className="p-4 rounded-xl bg-[var(--bg-elevated)] border-2 border-blue-600 dark:border-blue-500 shadow-sm">
              <span className="text-[11px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider block">
                Most Likely (P50)
              </span>
              <span className="font-mono text-2xl sm:text-3xl font-extrabold text-[var(--color-primary)] dark:text-blue-400 block mt-1">
                {Math.round(p50Hours).toLocaleString('en-US')} hrs
              </span>
              <span className="text-xs font-bold text-blue-700 dark:text-blue-300 block mt-0.5">
                {p50PM.formatted}
              </span>
              <span
                className="text-sm font-bold text-[var(--text-primary)] block mt-1 cursor-help"
                title={`$${Math.round(outputs.cost_likely_usd).toLocaleString('en-US')} USD`}
              >
                {fmtMoney(outputs.cost_likely_usd)}
                <span className="text-xs font-normal text-[var(--text-secondary)] ml-1.5">
                  ({rateLabel})
                </span>
              </span>
            </div>

            {/* p90 */}
            <div className="p-4 rounded-xl bg-[var(--bg-elevated)] border border-amber-500/20">
              <span className="text-[11px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider block">
                Conservative (P90)
              </span>
              <span className="font-mono text-xl sm:text-2xl font-bold text-[var(--text-primary)] block mt-1">
                {Math.round(p90Hours).toLocaleString('en-US')} hrs
              </span>
              <span className="text-xs font-semibold text-amber-700 dark:text-amber-300 block mt-0.5">
                {p90PM.formatted}
              </span>
              <span
                className="text-xs text-[var(--text-secondary)] block mt-1 cursor-help"
                title={`$${Math.round(outputs.cost_max_usd).toLocaleString('en-US')} USD`}
              >
                {fmtMoney(outputs.cost_max_usd)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Range Card: Clean Range Bar ── */}
      <Card variant="elevated" padding="lg">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <CardTitle as="h3" className="text-lg sm:text-xl font-bold flex items-center gap-2">
                <span>Effort ranges</span>
              </CardTitle>
              <CardDescription className="text-sm text-[var(--text-secondary)]">
                Likely range (middle half of outcomes) and plausible range (almost all outcomes)
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-2">
          {/* Visual Range Bar with clean stacked labels */}
          <ConfidenceRangeBar
            p10={p10Hours}
            p25={p25Hours}
            p50={p50Hours}
            p75={p75Hours}
            p90={p90Hours}
            unit="hours"
            formatValue={(val) => `${Math.round(val).toLocaleString('en-US')} hrs (${hoursToPersonMonths(val).formatted})`}
            showLabels
            showDetails
            ariaLabel="Effort range bar"
          />
        </CardContent>
      </Card>

      {/* ── Three Summary Tiles: Timeline, Cost Range, Risk ──── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Project Timeline */}
        <Card variant="elevated" padding="md" className="text-center">
          <div className="flex items-center justify-center gap-1.5 text-emerald-600 dark:text-emerald-400">
            <Clock size={18} />
            <span className="text-xs font-bold uppercase tracking-wider">
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

        {/* Cost Range */}
        <Card variant="elevated" padding="md" className="text-center">
          <div className="flex items-center justify-center gap-1.5 text-blue-600 dark:text-blue-400">
            <TrendingUp size={18} />
            <span className="text-xs font-bold uppercase tracking-wider">
              Cost Range
            </span>
          </div>
          <p className="font-mono text-xl sm:text-2xl font-bold text-[var(--color-primary)] mt-1">
            {fmtMoney(outputs.cost_min_usd)} – {fmtMoney(outputs.cost_max_usd)}
          </p>
          <span className="text-xs text-[var(--text-secondary)] mt-0.5 block">
            {rateLabel}
          </span>
        </Card>

        {/* Risk Profile */}
        <Card variant="elevated" padding="md" className="text-center">
          <div className="flex items-center justify-center gap-1.5" style={{ color: riskColor }}>
            <Shield size={18} />
            <span className="text-xs font-bold uppercase tracking-wider">
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
        <Card variant="elevated" padding="lg">
          <CardHeader>
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <CardTitle as="h3" className="text-lg font-bold flex items-center gap-2">
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
      <Card variant="elevated" padding="lg">
        <CardHeader className="pb-3">
          <CardTitle as="h3" className="text-base sm:text-lg font-bold flex items-center gap-2">
            <Layers size={18} className="text-[var(--text-secondary)]" />
            <span>Input Parameters</span>
          </CardTitle>
          <CardDescription className="text-xs text-[var(--text-secondary)]">
            Persisted inputs and project details.
          </CardDescription>
        </CardHeader>
        <CardContent className="mt-2 space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-xs">
            {[
              { label: 'Project Type', value: inputs.project_type },
              { label: 'Team Size', value: inputs.team_size?.toString() },
              { label: 'Duration', value: `${inputs.duration_months} months` },
              { label: 'Complexity', value: inputs.complexity },
              { label: 'Delivery Process', value: inputs.methodology },
              { label: 'Hourly Rate', value: `$${inputs.hourly_rate_usd}/hr` },
              { label: 'Features', value: inputs.feature_count ?? 'Not recorded' },
              { label: 'Integrations', value: inputs.integration_count ?? 'Not recorded' },
              { label: 'Requirements Volatility (1–5)', value: inputs.volatility_score ?? 'Not recorded' },
              { label: 'Team Experience (1–4)', value: inputs.team_experience ?? 'Not recorded' },
              { label: 'Function Points', value: displayFp },
            ].map((item, i) => (
              <div key={i} className="p-2.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
                <span className="text-[10px] uppercase font-bold text-[var(--text-tertiary)] block tracking-wider">
                  {item.label}
                </span>
                <span className="font-semibold text-[var(--text-primary)] text-xs mt-1 block">
                  {item.value}
                </span>
              </div>
            ))}
          </div>

          {/* Tech Stack Chip Wrap Container (Never cut off) */}
          <div className="p-3 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
            <span className="text-[10px] uppercase font-bold text-[var(--text-tertiary)] block tracking-wider mb-2">
              Technology Stack
            </span>
            <div className="flex flex-wrap gap-1.5">
              {inputs.tech_stack && inputs.tech_stack.length > 0 ? (
                inputs.tech_stack.map((tech, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-md text-xs font-medium bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-subtle)]"
                  >
                    {tech}
                  </span>
                ))
              ) : (
                <span className="text-xs text-[var(--text-tertiary)]">Not specified</span>
              )}
            </div>
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
