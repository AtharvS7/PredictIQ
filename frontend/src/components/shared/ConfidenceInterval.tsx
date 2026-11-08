import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './Card';
import { DataQualityBadge, type DataQualityTier, UncertaintyBadge } from './Badge';

export interface ConfidenceQuantiles {
  p10: number;
  p25?: number;
  p50: number;
  p75?: number;
  p90: number;
}

export interface ConfidenceRangeBarProps {
  p10: number;
  p25?: number;
  p50: number;
  p75?: number;
  p90: number;
  min?: number;
  max?: number;
  unit?: 'hours' | 'currency' | 'weeks' | 'months' | 'points' | 'custom';
  unitLabel?: string;
  formatValue?: (val: number) => string;
  currencySymbol?: string;
  showLabels?: boolean;
  showDetails?: boolean;
  compact?: boolean;
  className?: string;
  ariaLabel?: string;
}

export const ConfidenceRangeBar: React.FC<ConfidenceRangeBarProps> = ({
  p10,
  p25,
  p50,
  p75,
  p90,
  min: customMin,
  max: customMax,
  unit = 'hours',
  unitLabel,
  formatValue,
  currencySymbol = '$',
  showLabels = true,
  showDetails = true,
  compact = false,
  className = '',
  ariaLabel = 'Confidence interval range',
}) => {
  // Format numbers cleanly based on unit
  const format = (v: number): string => {
    if (formatValue) return formatValue(v);
    if (unit === 'currency') {
      return `${currencySymbol}${Math.round(v).toLocaleString('en-US')}`;
    }
    if (unit === 'hours') {
      return `${Math.round(v).toLocaleString('en-US')} hrs`;
    }
    if (unit === 'weeks') {
      return `${v.toFixed(1)} wks`;
    }
    if (unit === 'months') {
      return `${v.toFixed(1)} mo`;
    }
    if (unit === 'points') {
      return `${Math.round(v).toLocaleString('en-US')} FP`;
    }
    return unitLabel ? `${v.toLocaleString('en-US')} ${unitLabel}` : v.toLocaleString('en-US');
  };

  // Determine track bounds with safety margins (5% padding on edges)
  const autoMin = Math.max(0, p10 - (p90 - p10) * 0.15);
  const autoMax = p90 + (p90 - p10) * 0.15;
  const trackMin = customMin !== undefined ? customMin : autoMin;
  const trackMax = customMax !== undefined ? customMax : autoMax;
  const rangeSpan = trackMax - trackMin > 0 ? trackMax - trackMin : 1;

  // Percentage positions along the 0-100% horizontal track
  const p10Pct = Math.max(0, Math.min(100, ((p10 - trackMin) / rangeSpan) * 100));
  const p50Pct = Math.max(0, Math.min(100, ((p50 - trackMin) / rangeSpan) * 100));
  const p90Pct = Math.max(0, Math.min(100, ((p90 - trackMin) / rangeSpan) * 100));
  const bandWidth = Math.max(2, p90Pct - p10Pct);

  // Inner likely band (p25 to p75)
  const hasInner = p25 !== undefined && p75 !== undefined && p75 >= p25;
  const p25Pct = hasInner ? Math.max(0, Math.min(100, ((p25 - trackMin) / rangeSpan) * 100)) : null;
  const p75Pct = hasInner ? Math.max(0, Math.min(100, ((p75 - trackMin) / rangeSpan) * 100)) : null;
  const innerBandWidth = (hasInner && p25Pct !== null && p75Pct !== null) ? Math.max(2, p75Pct - p25Pct) : 0;

  // Compute spread metric
  const spreadRatio = p10 > 0 ? (p90 / p10).toFixed(1) : null;
  const deltaUpperPct = p50 > 0 ? Math.round(((p90 - p50) / p50) * 100) : 0;
  const deltaLowerPct = p50 > 0 ? Math.round(((p50 - p10) / p50) * 100) : 0;

  return (
    <div
      className={`confidence-range-container w-full ${className}`.trim()}
      role="group"
      aria-label={ariaLabel}
    >
      {/* Visual Bar Track */}
      <div className="relative pt-4 pb-2">
        {/* Track Background */}
        <div className="h-2.5 sm:h-3 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden relative border border-slate-300/40 dark:border-slate-700/60">
          {/* Calibrated Plausible Range (p10 to p90, 80% CI) */}
          <div
            className="absolute top-0 bottom-0 rounded-full transition-all duration-300 opacity-60"
            style={{
              left: `${p10Pct}%`,
              width: `${bandWidth}%`,
              background:
                'linear-gradient(90deg, rgba(16, 185, 129, 0.4) 0%, rgba(37, 99, 235, 0.4) 50%, rgba(245, 158, 11, 0.4) 100%)',
            }}
            title={`80% Plausible Range: ${format(p10)} to ${format(p90)}`}
          />

          {/* Calibrated Likely Band (p25 to p75, 50% CI) */}
          {hasInner && p25Pct !== null && (
            <div
              className="absolute top-0 bottom-0 rounded-full transition-all duration-300 shadow-sm"
              style={{
                left: `${p25Pct}%`,
                width: `${innerBandWidth}%`,
                background:
                  'linear-gradient(90deg, rgba(16, 185, 129, 0.85) 0%, rgba(37, 99, 235, 0.95) 50%, rgba(245, 158, 11, 0.85) 100%)',
              }}
              title={`50% Likely Band: ${format(p25)} to ${format(p75)}`}
            />
          )}
        </div>

        {/* p10 Marker Tick */}
        <div
          className="absolute top-2 w-0.5 h-6 -translate-x-1/2 bg-emerald-600 dark:bg-emerald-400 pointer-events-none rounded-full"
          style={{ left: `${p10Pct}%` }}
          aria-hidden="true"
        />

        {/* p50 Median Marker Pip */}
        <div
          className="absolute top-1.5 w-3.5 h-7 -translate-x-1/2 flex items-center justify-center pointer-events-none z-10"
          style={{ left: `${p50Pct}%` }}
          aria-hidden="true"
        >
          <div className="w-2.5 h-6 rounded-sm bg-blue-600 dark:bg-blue-400 shadow-[0_0_8px_rgba(37,99,235,0.6)] border border-white dark:border-slate-900" />
        </div>

        {/* p90 Marker Tick */}
        <div
          className="absolute top-2 w-0.5 h-6 -translate-x-1/2 bg-amber-600 dark:bg-amber-400 pointer-events-none rounded-full"
          style={{ left: `${p90Pct}%` }}
          aria-hidden="true"
        />
      </div>

      {/* Quantile Numerical Labels */}
      {showLabels && (
        <div className="flex justify-between items-start mt-1 gap-2 text-xs">
          {/* p10 */}
          <div className="flex flex-col items-start" style={{ width: '32%' }}>
            <span className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              p10 (Best Case)
            </span>
            <span className="font-mono text-sm font-bold text-[var(--text-primary)] tabular-nums mt-0.5">
              {format(p10)}
            </span>
            <span className="text-[10px] text-[var(--text-tertiary)]">
              -{deltaLowerPct}% from median
            </span>
          </div>

          {/* p50 & Inner Likely Band */}
          <div className="flex flex-col items-center text-center" style={{ width: '36%' }}>
            <span className="text-[11px] font-bold text-blue-700 dark:text-blue-400 uppercase tracking-wider flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              p50 (Median)
            </span>
            <span className="font-mono text-base font-extrabold text-[var(--color-primary)] dark:text-blue-400 tabular-nums mt-0.5">
              {format(p50)}
            </span>
            {hasInner ? (
              <span className="text-[10px] text-blue-600 dark:text-blue-400 font-medium">
                Likely: {format(p25)} – {format(p75)}
              </span>
            ) : (
              <span className="text-[10px] text-[var(--text-tertiary)]">
                calibrated center
              </span>
            )}
          </div>

          {/* p90 */}
          <div className="flex flex-col items-end text-right" style={{ width: '32%' }}>
            <span className="text-[11px] font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wider flex items-center gap-1 justify-end">
              p90 (Budget Cap)
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            </span>
            <span className="font-mono text-sm font-bold text-[var(--text-primary)] tabular-nums mt-0.5">
              {format(p90)}
            </span>
            <span className="text-[10px] text-[var(--text-tertiary)]">
              +{deltaUpperPct}% from median
            </span>
          </div>
        </div>
      )}

      {/* Uncertainty Spread Summary Banner */}
      {showDetails && !compact && spreadRatio && (
        <div className="mt-3 pt-2.5 border-t border-[var(--border-subtle)] space-y-1.5 text-xs text-[var(--text-secondary)]">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="inline-flex items-center gap-1.5">
              <span className="font-medium">Uncertainty Spread:</span>
              <span className="font-mono font-semibold text-[var(--text-primary)]">
                {spreadRatio}x (p90/p10)
              </span>
            </span>
            <span className="text-[11px] text-[var(--text-tertiary)]">
              50% Likely Band (Inner) [51.2% measured coverage] &bull; 80% Plausible Range (Outer) [79.0% holdout pooled coverage]
            </span>
          </div>
          <p className="text-[11px] text-[var(--text-tertiary)] leading-relaxed">
            <strong className="text-[var(--text-secondary)]">Uncertainty Guide:</strong> Typical error is roughly ±50% on novel projects. Use the 50% Likely Band (P25–P75) for expected sprint planning and target commitments, and the 80% Plausible Range (P10–P90) as your conservative risk ceiling / budget cap.
          </p>
        </div>
      )}
    </div>
  );
};

export interface ConfidenceIntervalCardProps {
  title: string;
  subtitle?: string;
  quantiles: ConfidenceQuantiles;
  unit?: 'hours' | 'currency' | 'weeks' | 'months' | 'points' | 'custom';
  unitLabel?: string;
  currencySymbol?: string;
  formatValue?: (val: number) => string;
  tier?: DataQualityTier;
  calibrated?: boolean;
  className?: string;
}

export const ConfidenceIntervalCard: React.FC<ConfidenceIntervalCardProps> = ({
  title,
  subtitle,
  quantiles,
  unit = 'hours',
  unitLabel,
  currencySymbol,
  formatValue,
  tier = 'B',
  calibrated = true,
  className = '',
}) => {
  return (
    <Card variant="default" padding="md" className={`confidence-interval-card ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex flex-col gap-0.5">
            <CardTitle as="h3">{title}</CardTitle>
            {subtitle && (
              <p className="text-xs text-[var(--text-secondary)]">{subtitle}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <DataQualityBadge tier={tier} compact />
            <UncertaintyBadge
              calibrated={calibrated}
              interval="80% CI"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <ConfidenceRangeBar
          p10={quantiles.p10}
          p25={quantiles.p25}
          p50={quantiles.p50}
          p75={quantiles.p75}
          p90={quantiles.p90}
          unit={unit}
          unitLabel={unitLabel}
          currencySymbol={currencySymbol}
          formatValue={formatValue}
          showLabels
          showDetails
        />
      </CardContent>
    </Card>
  );
};

export default ConfidenceRangeBar;
