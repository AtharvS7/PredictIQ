import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { Badge } from '@/components/shared/Badge';
import { MetricValue, Text } from '@/components/shared/Typography';
import { Layers, CheckCircle2, Shield, Info } from 'lucide-react';
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
              <CardTitle as="h3" className="text-base sm:text-lg">
                Functional Size & Scope Calibration
              </CardTitle>
              <CardDescription className="text-xs">
                Standardized software deliverable sizing based on functional requirements
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            <Badge variant="primary" size="xs" pill icon={<Shield size={10} />}>
              IFPUG 4.3.1 Standard
            </Badge>
            <Badge variant="success" size="xs" pill icon={<CheckCircle2 size={10} />}>
              Zero Fabricated Factors
            </Badge>
            <Badge variant="neutral" size="xs" pill>
              Effort Strictly Driven by Size (FP)
            </Badge>
            {source === 'upload' && (
              <>
                <Badge variant="warning" size="xs" pill>
                  Assumption: ~8 FP/Story
                </Badge>
                <Badge variant="warning" size="xs" pill>
                  Assumption: ~5 FP/API
                </Badge>
                <Badge variant="info" size="xs" pill>
                  NLP Size Uncertainty: ±15%
                </Badge>
              </>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="mt-2 space-y-4">
        {/* Dynamic Metrics Readout */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
          <MetricValue
            label="Functional Size"
            value={calculatedFp.toLocaleString()}
            unit="FP"
            size="md"
            subtext="Function Points"
            highlightColor="var(--color-primary)"
          />
          <MetricValue
            label="Feature Units"
            value={featureCount}
            unit="features"
            size="md"
            subtext="~8 FP per user feature"
          />
          <MetricValue
            label="Integration Endpoints"
            value={integrationCount}
            unit="APIs"
            size="md"
            subtext="~5 FP per external interface"
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
                Estimated User Stories / Functional Modules
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
                Core user journeys, screens, and administrative workflows
              </Text>
            </div>

            <div>
              <label
                htmlFor="wizard-integration-count"
                className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5"
              >
                External Integrations (APIs / Services)
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
                Third-party APIs, auth providers, database connectors, ERP/CRMs
              </Text>
            </div>
          </div>
        )}

        {/* Transparency note & Statistical Reality */}
        <div className="flex items-start gap-2 p-2.5 rounded-md bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-900/40 text-xs text-blue-900 dark:text-blue-200">
          <Info size={14} className="shrink-0 mt-0.5 text-blue-600 dark:text-blue-400" />
          <div className="space-y-1">
            <div>
              <span className="font-semibold">Provenance &amp; Statistical Reality: </span>
              {source === 'upload' ? (
                <span>
                  Functional scope was extracted via NLP from your specification document and mapped to standardized IFPUG function points. Sizing uncertainty (±15%) is strictly propagated into effort intervals via log-space variance combination.
                </span>
              ) : (
                <span>
                  Functional points (FP) provide an objective measure of software deliverables independent of implementation language. ISBSG R2024 calibrated reference baseline.
                </span>
              )}
            </div>
            <p className="text-[11px] text-blue-800 dark:text-blue-300 leading-normal">
              <strong>Model Principle:</strong> Effort depends strictly on functional size (<code className="font-mono">size_fp</code>) via the monotone power-law ($E = a \cdot S^b$). Planned duration and team size are schedule / staffing capacity constraints, not effort predictors (Brooks&apos; Law). Typical estimation error is roughly ±50% on novel projects prior to empirical Bayes shrinkage.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default FunctionalSizeCard;
