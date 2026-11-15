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
      padding="md"
      className={`planning-capacity-card border-t-4 border-t-indigo-600 dark:border-t-indigo-500 ${className}`.trim()}
    >
      <CardHeader>
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400">
              <Users size={18} />
            </div>
            <div>
              <CardTitle as="h3" className="text-base sm:text-lg">
                Team and schedule
              </CardTitle>
              <CardDescription className="text-xs">
                Used to show staffing and cost over time.
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="mt-2 space-y-4">
        {/* Real-time Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
          <MetricValue
            label="Team capacity (hours)"
            value={totalCapacityHours.toLocaleString('en-US')}
            size="md"
            highlightColor="var(--color-primary)"
          />

          <MetricValue
            label="Cost at your rate"
            value={`${currencySymbol}${Math.round(baselineCostConverted).toLocaleString('en-US')}`}
            unit={currencyCode}
            size="md"
          />

          <MetricValue
            label="Cost per month"
            value={`${currencySymbol}${Math.round(monthlyRunRateConverted).toLocaleString('en-US')}`}
            unit={`/mo`}
            size="md"
          />
        </div>

        {/* High team size notice if applicable */}
        {isHighTeamSize && (
          <div className="flex items-start gap-2 p-2.5 rounded-md bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-200">
            <AlertCircle size={14} className="shrink-0 mt-0.5 text-amber-600 dark:text-amber-400" />
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
