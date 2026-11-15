import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { MetricValue, Text } from '@/components/shared/Typography';
import { Layers, Info } from 'lucide-react';
import { estimateFunctionPoints } from './estimateUtils';

export interface FunctionalSizeCardProps {
  featureCount: number;
  integrationCount: number;
  customFp?: number | null;
  onFeatureChange?: (count: number) => void;
  onIntegrationChange?: (count: number) => void;
  readOnly?: boolean;
  source?: 'upload' | 'manual';
  className?: string;
}

export const FunctionalSizeCard: React.FC<FunctionalSizeCardProps> = ({
  featureCount,
  integrationCount,
  customFp,
  onFeatureChange,
  onIntegrationChange,
  readOnly = false,
  source = 'manual',
  className = '',
}) => {
  const calculatedFp = customFp ?? estimateFunctionPoints(featureCount, integrationCount);

  return (
    <Card
      variant="elevated"
      padding="md"
      className={`functional-size-card border-l-4 border-l-blue-600 dark:border-l-blue-500 ${className}`.trim()}
    >
      <CardHeader>
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/70 text-blue-600 dark:text-blue-400">
              <Layers size={18} />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <CardTitle as="h3" className="text-base sm:text-lg">
                  Project size
                </CardTitle>
                <span
                  title="Size is estimated from your features and integrations. You can edit it."
                  className="cursor-help text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] inline-flex items-center"
                  aria-label="Size is estimated from your features and integrations. You can edit it."
                >
                  <Info size={15} />
                </span>
              </div>
              <CardDescription className="text-xs">
                Tell us about your project, or upload a requirements document.
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="mt-2 space-y-4">
        {/* Dynamic Metrics Readout */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
          <MetricValue
            label="Project size"
            value={calculatedFp.toLocaleString()}
            unit="FP"
            size="md"
            highlightColor="var(--color-primary)"
          />
          <MetricValue
            label="Features"
            value={featureCount}
            size="md"
          />
          <MetricValue
            label="Integrations"
            value={integrationCount}
            size="md"
          />
        </div>

        {/* Interactive Controls if not readOnly */}
        {!readOnly && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
            <div>
              <label
                htmlFor="wizard-feature-count"
                className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5"
              >
                Number of features / user stories
              </label>
              <input
                id="wizard-feature-count"
                type="number"
                min={1}
                max={250}
                value={featureCount}
                onChange={(e) => onFeatureChange?.(Math.max(1, Number(e.target.value)))}
                className="w-full px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] transition"
              />
              <Text variant="caption" className="mt-1">
                Core screens and workflows
              </Text>
            </div>

            <div>
              <label
                htmlFor="wizard-integration-count"
                className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5"
              >
                Number of external integrations
              </label>
              <input
                id="wizard-integration-count"
                type="number"
                min={0}
                max={15}
                value={integrationCount}
                onChange={(e) => onIntegrationChange?.(Math.max(0, Math.min(15, Number(e.target.value))))}
                className="w-full px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] transition"
              />
              <Text variant="caption" className="mt-1">
                Payment, email, login or other third-party services
              </Text>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FunctionalSizeCard;
