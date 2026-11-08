import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { Badge } from '@/components/shared/Badge';
import { MetricValue, Text } from '@/components/shared/Typography';
import { Users, Clock, DollarSign, Target, Sparkles, AlertCircle } from 'lucide-react';
import { hoursToPersonMonths, HOURS_PER_PERSON_MONTH } from './estimateUtils';

export interface PlanningCapacityCardProps {
  teamSize: number;
  durationMonths: number;
  hourlyRateUsd: number;
  currencySymbol?: string;
  currencyRate?: number;
  currencyCode?: string;
  className?: string;
}

export const PlanningCapacityCard: React.FC<PlanningCapacityCardProps> = ({
  teamSize,
  durationMonths,
  hourlyRateUsd,
  currencySymbol = '$',
  currencyRate = 1,
  currencyCode = 'USD',
  className = '',
}) => {
  // Real-time reactive calculations
  const safeTeam = Math.max(1, teamSize || 1);
  const safeDuration = Math.max(0.5, durationMonths || 1);
  const safeRate = Math.max(10, hourlyRateUsd || 75);

  const totalCapacityHours = Math.round(safeTeam * safeDuration * HOURS_PER_PERSON_MONTH);
  const personMonthsData = hoursToPersonMonths(totalCapacityHours);
  const baselineCostUsd = totalCapacityHours * safeRate;
  const baselineCostConverted = baselineCostUsd * currencyRate;
  const monthlyRunRateConverted = safeTeam * HOURS_PER_PERSON_MONTH * safeRate * currencyRate;

  const isHighTeamSize = safeTeam > 25;

  return (
    <Card
      variant="elevated"
      padding="md"
      className={`planning-capacity-card border-t-4 border-t-indigo-600 dark:border-t-indigo-500 ${className}`.trim()}
    >
      <CardHeader>
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400">
              <Target size={18} />
            </div>
            <div>
              <CardTitle as="h3" className="text-base sm:text-lg">
                Planning Parameters & Capacity Target
              </CardTitle>
              <CardDescription className="text-xs">
                Real-time capacity and budget baseline for your target planning horizon
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            <Badge variant="info" size="xs" pill icon={<Clock size={10} />}>
              152 hrs / Person-Month
            </Badge>
            <Badge variant="neutral" size="xs" pill icon={<Sparkles size={10} />}>
              Reactive Planning
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="mt-2 space-y-4">
        {/* Real-time Reactive Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
          <MetricValue
            label="Planned Capacity"
            value={totalCapacityHours.toLocaleString('en-US')}
            unit="hours"
            size="md"
            subtext={`${personMonthsData.formatted} across ${safeDuration} mo target`}
            highlightColor="var(--color-primary)"
          />

          <MetricValue
            label="Baseline Target Budget"
            value={`${currencySymbol}${Math.round(baselineCostConverted).toLocaleString('en-US')}`}
            unit={currencyCode}
            size="md"
            subtext={`@ ${currencySymbol}${(safeRate * currencyRate).toFixed(0)}/hr baseline`}
          />

          <MetricValue
            label="Monthly Run-Rate"
            value={`${currencySymbol}${Math.round(monthlyRunRateConverted).toLocaleString('en-US')}`}
            unit={`/mo`}
            size="md"
            subtext={`${safeTeam} full-time engineers`}
          />
        </div>

        {/* Clear target planning horizon disclaimer */}
        <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs text-[var(--text-secondary)] space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-[var(--text-primary)]">
            <Target size={14} className="text-indigo-600 dark:text-indigo-400" />
            <span>Target Planning Labeling &amp; Integrity:</span>
          </div>
          <p className="leading-relaxed">
            <strong className="text-[var(--text-primary)]">Planned Target Duration</strong> reflects your scheduled delivery deadline (target planning horizon),
            <em className="text-indigo-600 dark:text-indigo-400 font-medium not-italic"> not</em> the ML model&apos;s predicted effort duration.
            Team Size and Duration are schedule and staffing capacity planning indicators, <em className="text-indigo-600 dark:text-indigo-400 font-medium not-italic">NOT</em> effort predictors. In accordance with Brooks&apos; Law, adding engineers does not linearly compress effort. The model computes independent effort bounds driven strictly by functional size (<code className="font-mono">size_fp</code>).
          </p>
          <p className="text-[11px] text-[var(--text-tertiary)] pt-0.5">
            Zero fabricated complexity factors: No arbitrary multiplier tables or artificial padding are added to these constraints.
          </p>
        </div>

        {/* High team size notice if applicable */}
        {isHighTeamSize && (
          <div className="flex items-start gap-2 p-2.5 rounded-md bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-200">
            <AlertCircle size={14} className="shrink-0 mt-0.5 text-amber-600 dark:text-amber-400" />
            <div>
              <span className="font-semibold">Coordination Note: </span>
              A team of {safeTeam} members exceeds typical agile pod sizes (3–12). Larger teams involve non-linear communication overhead (Brooks&apos; Law).
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PlanningCapacityCard;
