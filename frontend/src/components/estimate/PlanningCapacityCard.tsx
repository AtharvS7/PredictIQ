import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { MetricValue } from '@/components/shared/Typography';
import { Users, AlertCircle } from 'lucide-react';
import { HOURS_PER_PERSON_MONTH } from './estimateUtils';

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
  const safeTeam = Math.max(1, teamSize || 1);
  const safeDuration = Math.max(0.5, durationMonths || 1);
  const safeRate = Math.max(10, hourlyRateUsd || 75);

  const totalCapacityHours = Math.round(safeTeam * safeDuration * HOURS_PER_PERSON_MONTH);
  const baselineCostUsd = totalCapacityHours * safeRate;
  const baselineCostConverted = baselineCostUsd * currencyRate;
  const monthlyRunRateConverted = safeTeam * HOURS_PER_PERSON_MONTH * safeRate * currencyRate;

  const isHighTeamSize = safeTeam > 25;

  return (
    <Card
      variant="elevated"
      padding="lg"
      className={`planning-capacity-card border-t-4 border-t-indigo-600 dark:border-t-indigo-500 ${className}`.trim()}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400">
              <Users size={20} />
            </div>
            <div>
              <CardTitle as="h3" className="text-lg sm:text-xl font-bold">
                Team and schedule
              </CardTitle>
              <CardDescription className="text-sm text-[var(--text-secondary)] mt-0.5">
                Used to show staffing and cost over time.
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="mt-2 space-y-4">
        {/* Real-time Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 sm:p-5 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
          <div className="p-3.5 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] flex flex-col justify-center">
            <MetricValue
              label="Team capacity"
              value={totalCapacityHours.toLocaleString('en-US')}
              unit="hours"
              size="md"
              highlightColor="var(--color-primary)"
            />
          </div>

          <div className="p-3.5 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] flex flex-col justify-center">
            <MetricValue
              label="Cost at your rate"
              value={`${currencySymbol}${Math.round(baselineCostConverted).toLocaleString('en-US')}`}
              unit={currencyCode}
              size="md"
            />
          </div>

          <div className="p-3.5 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] flex flex-col justify-center">
            <MetricValue
              label="Cost per month"
              value={`${currencySymbol}${Math.round(monthlyRunRateConverted).toLocaleString('en-US')}`}
              unit="/mo"
              size="md"
            />
          </div>
        </div>

        {/* High team size notice if applicable */}
        {isHighTeamSize && (
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-200">
            <AlertCircle size={15} className="shrink-0 mt-0.5 text-amber-600 dark:text-amber-400" />
            <div>
              <span className="font-semibold">Team size note: </span>
              A team of {safeTeam} is larger than typical teams (3–12).
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PlanningCapacityCard;
