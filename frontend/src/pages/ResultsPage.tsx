import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import SEOHead from '@/components/shared/SEOHead';
import CurrencySelector from '@/components/shared/CurrencySelector';
import { useEstimateStore } from '@/store/estimateStore';
import { useCurrencyStore } from '@/store/currencyStore';
import { useToast } from '@/App';
import { useTheme } from '@/components/ThemeProvider';
import { exportPDF, exportJSON, duplicateEstimate, createShareLink } from '@/lib/api';
import { RISK_COLORS } from '@/lib/risk';
import { Bar, PolarArea, Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  RadialLinearScale, ArcElement, PointElement, LineElement, Filler,
  Tooltip as ChartTooltip, Legend,
} from 'chart.js';
import {
  Download, FileDown, Copy, Share2, ArrowLeft, Clock,
  Shield, TrendingUp, AlertTriangle, Info, FileText,
  BarChart3, PieChart, CircleDot, LineChart, CheckCircle2,
  HelpCircle,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { Badge, DataQualityBadge, UncertaintyBadge, ModelVersionBadge } from '@/components/shared/Badge';
import { ConfidenceRangeBar } from '@/components/shared/ConfidenceInterval';
import {
  hoursToPersonMonths,
  determineDataQualityTier,
  checkIsOOD,
  TIER_PROVENANCE,
} from '@/components/estimate/estimateUtils';
import { ModelTransparencyModal } from '@/components/estimate/ModelTransparencyModal';
import { OODDiagnosticsCard } from '@/components/estimate/OODDiagnosticsCard';
import { formatEstimateToV2Contract } from '@/components/estimate/exportContractUtils';

/* ── Chart.js Registration ─────────────────────────────────────────────── */
ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  RadialLinearScale, ArcElement, PointElement, LineElement, Filler,
  ChartTooltip, Legend,
);

const PHASE_COLORS = ['#1A56DB', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

/** Read a CSS custom property's computed value — Chart.js can't parse var() tokens. */
function getThemeColor(varName: string, fallback: string): string {
  if (typeof document === 'undefined') return fallback;
  const value = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
  return value || fallback;
}

type ChartType = 'bar' | 'polar' | 'pie' | 'line';

export default function ResultsPage() {
  // Canvas colors must be recomputed when appearance or system preference changes.
  useTheme();
  const { id } = useParams<{ id: string }>();
  const { currentEstimate, loading, error, fetchEstimate } = useEstimateStore();
  const { format, convert, symbol } = useCurrencyStore();
  const sym = symbol();
  const { addToast } = useToast();
  const [chartType, setChartType] = useState<ChartType>('bar');
  const [showTierModal, setShowTierModal] = useState(false);
  const [showTransparencyModal, setShowTransparencyModal] = useState(false);

  useEffect(() => {
    if (id) fetchEstimate(id);
  }, [id, fetchEstimate]);

  const handleExportPDF = async () => {
    if (!id) return;
    try {
      const currencyCode = useCurrencyStore.getState().currency;
      const response = await exportPDF(id, currencyCode);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `PredictIQ_Estimate_${id.slice(0, 8)}_${currencyCode}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      addToast('success', 'PDF exported!');
    } catch {
      addToast('error', 'PDF export failed');
    }
  };

  const handleExportJSON = async () => {
    if (!id || !currentEstimate) return;
    try {
      const currencyCode = useCurrencyStore.getState().currency;
      const currencyRate = convert(1);
      // Format estimate strictly adhering to api_estimate_v2.json contract
      const v2Payload = formatEstimateToV2Contract(currentEstimate, currencyCode, currencyRate);
      const blob = new Blob([JSON.stringify(v2Payload, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PredictIQ_Estimate_${id.slice(0, 8)}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
      addToast('success', 'Contract-compliant JSON exported!');
    } catch {
      addToast('error', 'JSON export failed');
    }
  };

  const handleCopyJSON = async () => {
    if (!currentEstimate) return;
    try {
      const currencyCode = useCurrencyStore.getState().currency;
      const currencyRate = convert(1);
      const v2Payload = formatEstimateToV2Contract(currentEstimate, currencyCode, currencyRate);
      await navigator.clipboard.writeText(JSON.stringify(v2Payload, null, 2));
      addToast('success', 'JSON contract payload copied to clipboard!');
    } catch {
      addToast('error', 'Failed to copy JSON to clipboard');
    }
  };

  const handleDuplicate = async () => {
    if (!id) return;
    try {
      await duplicateEstimate(id);
      addToast('success', 'Estimate duplicated');
    } catch {
      addToast('error', 'Duplication failed');
    }
  };

  const handleShare = async () => {
    if (!id) return;
    try {
      const { data } = await createShareLink(id, { expires_in_days: 7 });
      await navigator.clipboard.writeText(window.location.origin + data.share_url);
      addToast('success', 'Share link copied to clipboard!');
    } catch {
      addToast('error', 'Failed to create share link');
    }
  };

  if (!loading && (error || !currentEstimate)) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
        <Navbar />
        <div style={{ display: 'flex' }}>
          <Sidebar />
          <main style={{ flex: 1, padding: '2rem' }}>
            <div role="alert">
              <h1>Unable to load estimate</h1>
              <p>{error || 'This estimate is unavailable.'}</p>
              {id && <button className="btn-primary" onClick={() => fetchEstimate(id)}>Try again</button>}
              <Link to="/estimates">Back to estimates</Link>
            </div>
          </main>
        </div>
      </div>
    );
  }

  if (loading || !currentEstimate) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
        <Navbar />
        <div style={{ display: 'flex' }}>
          <Sidebar />
          <main style={{ flex: 1, padding: '2rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[200, 120, 300, 200].map((h, i) => (
                <div key={i} className="skeleton" style={{ height: h, borderRadius: 16 }} />
              ))}
            </div>
          </main>
        </div>
      </div>
    );
  }

  const { inputs, outputs, model_version } = currentEstimate;
  const phaseData = outputs.phase_breakdown.map((p, i) => ({
    name: p.phase.replace('& ', '').split(' ')[0],
    fullName: p.phase,
    hours: p.effort_hours,
    cost: convert(p.cost_usd),
    pct: p.pct_of_total,
    fill: PHASE_COLORS[i % PHASE_COLORS.length],
  }));

  const riskColor = RISK_COLORS[outputs.risk_level] || '#64748B';
  const tier = determineDataQualityTier(model_version, inputs);
  const tierInfo = TIER_PROVENANCE[tier];
  const oodStatus = checkIsOOD(inputs);
  const isCalibrated = model_version.startsWith('production-v3-') || tier !== 'C';

  const p10Hours = outputs.effort_min_hours;
  const p50Hours = outputs.effort_likely_hours;
  const p90Hours = outputs.effort_max_hours;
  const p25Hours = outputs.effort_p25_hours ?? outputs.effort_hours?.p25;
  const p75Hours = outputs.effort_p75_hours ?? outputs.effort_hours?.p75;

  const p10PM = hoursToPersonMonths(p10Hours);
  const p50PM = hoursToPersonMonths(p50Hours);
  const p90PM = hoursToPersonMonths(p90Hours);

  /* ── Shared Chart Config ─────────────────────────────────────────────── */
  const tooltipConfig = {
    backgroundColor: 'rgba(30, 41, 59, 0.95)',
    titleColor: '#F1F5F9',
    bodyColor: '#F1F5F9',
    borderColor: 'rgba(255,255,255,0.1)',
    borderWidth: 1,
    cornerRadius: 10,
    padding: 12,
    titleFont: { size: 13, weight: 'bold' as const },
    bodyFont: { size: 12 },
    callbacks: {
      label: (ctx: { raw: unknown }) => `Cost: ${format(Number(ctx.raw) / convert(1))}`,
    },
  };

  const textSecondary = getThemeColor('--text-secondary', '#94A3B8');
  const textPrimary = getThemeColor('--text-primary', '#F1F5F9');
  const borderColor = getThemeColor('--border-color', '#334155');

  const legendConfig = {
    position: 'right' as const,
    labels: {
      color: textPrimary,
      font: { size: 12 },
      padding: 14,
      usePointStyle: true,
      pointStyleWidth: 10,
    },
  };

  const labels = phaseData.map(p => p.name);
  const costValues = phaseData.map(p => p.cost);
  const bgColors = phaseData.map(p => p.fill);
  const bgColorsAlpha = bgColors.map(c => c + 'CC');

  /* ── Chart Toggle Buttons ────────────────────────────────────────────── */
  const chartOptions: { key: ChartType; icon: React.ReactNode; label: string }[] = [
    { key: 'bar', icon: <BarChart3 size={14} />, label: 'Bar' },
    { key: 'polar', icon: <CircleDot size={14} />, label: 'Polar' },
    { key: 'pie', icon: <PieChart size={14} />, label: 'Pie' },
    { key: 'line', icon: <LineChart size={14} />, label: 'Line' },
  ];

  /* ── Render Active Chart ─────────────────────────────────────────────── */
  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return (
          <Bar
            data={{
              labels,
              datasets: [{
                label: 'Cost',
                data: costValues,
                backgroundColor: bgColors,
                borderRadius: 6,
                borderSkipped: false,
              }],
            }}
            options={{
              indexAxis: 'y' as const,
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false },
                tooltip: tooltipConfig,
              },
              scales: {
                x: {
                  ticks: {
                    color: textSecondary,
                    callback: (v) => `${sym}${(Number(v) / 1000).toFixed(0)}k`,
                  },
                  grid: { color: borderColor },
                },
                y: {
                  ticks: { color: textSecondary, font: { size: 12 } },
                  grid: { display: false },
                },
              },
            }}
          />
        );
      case 'polar':
        return (
          <PolarArea
            data={{
              labels: phaseData.map(p => p.fullName),
              datasets: [{
                data: costValues,
                backgroundColor: bgColorsAlpha,
                borderColor: bgColors,
                borderWidth: 2,
              }],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: legendConfig,
                tooltip: tooltipConfig,
              },
              scales: {
                r: {
                  ticks: { display: false },
                  grid: { color: borderColor },
                },
              },
            }}
          />
        );
      case 'pie':
        return (
          <Pie
            data={{
              labels: phaseData.map(p => p.fullName),
              datasets: [{
                data: costValues,
                backgroundColor: bgColorsAlpha,
                borderColor: bgColors,
                borderWidth: 2,
                hoverOffset: 8,
              }],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: legendConfig,
                tooltip: tooltipConfig,
              },
            }}
          />
        );
      case 'line':
        return (
          <Line
            data={{
              labels,
              datasets: [{
                label: 'Cost',
                data: costValues,
                borderColor: '#1A56DB',
                backgroundColor: 'rgba(26, 86, 219, 0.15)',
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointBackgroundColor: bgColors,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
              }],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false },
                tooltip: tooltipConfig,
              },
              scales: {
                x: {
                  ticks: { color: textSecondary, maxRotation: 30 },
                  grid: { color: borderColor },
                },
                y: {
                  ticks: {
                    color: textSecondary,
                    callback: (v) => `${sym}${(Number(v) / 1000).toFixed(0)}k`,
                  },
                  grid: { color: borderColor },
                },
              },
            }}
          />
        );
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <SEOHead title="Estimate Results" description="View detailed cost breakdown, timeline, risk analysis, and phase-by-phase estimates for your project." />
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: 1100, margin: '0 auto' }}>
          {/* Header */}
          <div className="animate-fade-in" style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
            marginBottom: 24, flexWrap: 'wrap', gap: 12,
          }}>
            <div>
              <Link to="/estimates" style={{
                display: 'inline-flex', alignItems: 'center', gap: 4,
                color: 'var(--text-secondary)', fontSize: '0.8125rem', textDecoration: 'none',
                marginBottom: 8,
              }}>
                <ArrowLeft size={14} /> Back to estimates
              </Link>
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <button
                  type="button"
                  className="cursor-pointer border-0 bg-transparent p-0 inline-flex items-center"
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
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {currentEstimate.project_name}
              </h1>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                {inputs.project_type} • v{currentEstimate.version} •
                {new Date(currentEstimate.created_at).toLocaleDateString()}
              </p>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setShowTransparencyModal(true)}
                title="View model architecture, empirical benchmarks, and calibration provenance"
                data-testid="how-it-works-button"
              >
                <HelpCircle size={15} className="text-blue-600 dark:text-blue-400" />
                <span>How this estimate works</span>
              </button>
              <CurrencySelector />
              <button className="btn-secondary" onClick={handleExportPDF}><Download size={15} /> PDF ({sym})</button>
              <button className="btn-secondary" onClick={handleExportJSON} data-testid="export-json-button"><FileDown size={15} /> JSON</button>
              <button className="btn-secondary" onClick={handleCopyJSON} data-testid="copy-json-button"><Copy size={15} /> Copy JSON</button>
              <button className="btn-secondary" onClick={handleShare}><Share2 size={15} /> Share</button>
              <button className="btn-secondary" onClick={handleDuplicate}><Copy size={15} /> Duplicate</button>
            </div>
          </div>

          {/* Data Provenance Details Card (collapsible / tooltip) */}
          {showTierModal && (
            <Card variant="subtle" padding="sm" className="mb-4 border-blue-200 dark:border-blue-900 bg-blue-50/60 dark:bg-blue-950/30 text-xs">
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

          {/* Out of Distribution (OOD) Guidance & Explanations */}
          <OODDiagnosticsCard inputs={inputs} reasons={oodStatus.reasons} className="mb-5" />

          {/* Calibrated Confidence Range Bar Card */}
          <Card variant="elevated" padding="md" className="mb-5 border-t-4 border-t-[var(--color-primary)]">
            <CardHeader>
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <CardTitle as="h3" className="text-lg font-bold flex items-center gap-2">
                    <span>Calibrated Effort Ranges</span>
                    <span className="text-xs font-normal text-[var(--text-secondary)]">
                      (Hours &amp; Person-Months at 152 hrs/PM)
                    </span>
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Visual uncertainty range with calibrated median marker and p10–p90 bounds
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="primary" size="xs" pill>
                    152 hrs = 1 Person-Month
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-2">
              <ConfidenceRangeBar
                p10={p10Hours}
                p25={p25Hours}
                p50={p50Hours}
                p75={p75Hours}
                p90={p90Hours}
                unit="hours"
                formatValue={(val) => `${Math.round(val).toLocaleString()} hrs (${hoursToPersonMonths(val).formatted})`}
                showLabels
                showDetails
                ariaLabel="Calibrated prediction ranges"
              />
            </CardContent>
          </Card>

          {/* Cost Summary (with person-months) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))', gap: 16, marginBottom: 20 }}>
            {[
              {
                label: 'Optimistic (p10)',
                value: outputs.cost_min_usd,
                color: '#10B981',
                sub: `${outputs.effort_min_hours.toLocaleString()} hrs (${p10PM.formatted})`,
              },
              {
                label: 'Most Likely (p50)',
                value: outputs.cost_likely_usd,
                color: '#1A56DB',
                sub: `${outputs.effort_likely_hours.toLocaleString()} hrs (${p50PM.formatted})`,
                primary: true,
              },
              {
                label: 'Conservative (p90)',
                value: outputs.cost_max_usd,
                color: '#F59E0B',
                sub: `${outputs.effort_max_hours.toLocaleString()} hrs (${p90PM.formatted})`,
              },
            ].map((card, i) => (
              <div key={i} className="card" style={{
                padding: 24, textAlign: 'center',
                border: card.primary ? `2px solid ${card.color}` : undefined,
              }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {card.label}
                </p>
                <p style={{ fontSize: card.primary ? '2rem' : '1.5rem', fontWeight: 700, color: card.color, marginTop: 4 }}>
                  {format(card.value)}
                </p>
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                  {card.sub}
                </p>
              </div>
            ))}
          </div>

          {/* Confidence + Timeline + Risk row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))', gap: 16, marginBottom: 20 }}>
            {/* Confidence */}
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <TrendingUp size={20} color="var(--color-primary)" />
              <p style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)', marginTop: 4 }}>
                {outputs.confidence_pct.toFixed(0)}%
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{currentEstimate.model_version.startsWith('production-v3-') ? 'Validation interval coverage' : 'Heuristic confidence'}</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{currentEstimate.model_version.startsWith('production-v3-') ? 'Observed coverage on held-out projects; not a guarantee for this estimate.' : 'This score and effort range are not calibrated probabilities.'}</p>
            </div>

            {/* Timeline */}
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <Clock size={20} color="#10B981" />
              <p style={{ fontSize: '1.75rem', fontWeight: 700, color: '#10B981', marginTop: 4 }}>
                {outputs.timeline_likely_weeks.toFixed(0)} wks
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                {outputs.timeline_min_weeks.toFixed(0)}–{outputs.timeline_max_weeks.toFixed(0)} range
              </p>
            </div>

            {/* Risk Score */}
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <Shield size={20} color={riskColor} />
              <p style={{ fontSize: '1.75rem', fontWeight: 700, color: riskColor, marginTop: 4 }}>
                {outputs.risk_score.toFixed(0)}/100
              </p>
              <p style={{ fontSize: '0.75rem' }}>
                <span className={`risk-badge risk-${outputs.risk_level.toLowerCase()}`}>
                  {outputs.risk_level} Risk
                </span>
              </p>
            </div>
          </div>

          {/* Phase Breakdown Chart */}
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
              <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                <TrendingUp size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
                Phase Breakdown
              </h3>
              {/* Chart Type Switcher */}
              <div style={{
                display: 'flex', gap: 4, flexWrap: 'wrap',
                background: 'var(--bg-elevated)', borderRadius: 10, padding: 3,
              }}>
                {chartOptions.map(opt => (
                  <button
                    key={opt.key}
                    aria-pressed={chartType === opt.key}
                    onClick={() => setChartType(opt.key)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 4,
                      padding: '6px 12px', minHeight: 44, borderRadius: 8, border: 'none',
                      fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      background: chartType === opt.key ? 'var(--color-primary)' : 'transparent',
                      color: chartType === opt.key ? '#fff' : 'var(--text-secondary)',
                    }}
                  >
                    {opt.icon} {opt.label}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ height: 280 }}>
              {renderChart()}
            </div>

            {/* Phase Table */}
            <div style={{ marginTop: 16, overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 4px', fontSize: '0.8125rem' }}>
                <thead>
                  <tr style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.6875rem' }}>
                    <th style={{ textAlign: 'left', padding: '8px 12px' }}>Phase</th>
                    <th style={{ textAlign: 'right', padding: '8px 12px' }}>Effort (hrs)</th>
                    <th style={{ textAlign: 'right', padding: '8px 12px' }}>Cost</th>
                    <th style={{ textAlign: 'right', padding: '8px 12px' }}>Duration (wks)</th>
                    <th style={{ textAlign: 'right', padding: '8px 12px' }}>% Total</th>
                  </tr>
                </thead>
                <tbody>
                  {outputs.phase_breakdown.map((phase, i) => (
                    <tr key={i} style={{ background: i % 2 === 0 ? 'var(--bg-elevated)' : 'transparent', borderRadius: 8 }}>
                      <td style={{ padding: '8px 12px', fontWeight: 500, color: 'var(--text-primary)' }}>
                        <span style={{
                          display: 'inline-block', width: 8, height: 8, borderRadius: 2,
                          background: PHASE_COLORS[i], marginRight: 8,
                        }} />
                        {phase.phase}
                      </td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', color: 'var(--text-secondary)' }}>{phase.effort_hours.toLocaleString()}</td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', color: 'var(--text-primary)', fontWeight: 500 }}>{format(phase.cost_usd)}</td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', color: 'var(--text-secondary)' }}>{phase.duration_weeks}</td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', color: 'var(--text-secondary)' }}>{phase.pct_of_total}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Risk Panel + Insights */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 300px), 1fr))', gap: 20, marginBottom: 20 }}>
            {/* Risks */}
            <div className="card" style={{ padding: 24 }}>
              <h3 style={{ fontWeight: 600, marginBottom: 16, color: 'var(--text-primary)' }}>
                <AlertTriangle size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
                Top Risk Factors
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {outputs.top_risks.map((risk, i) => {
                  const sevColor = RISK_COLORS[risk.severity];
                  return (
                    <div key={i} style={{
                      padding: '10px 12px', borderRadius: 10,
                      background: 'var(--bg-elevated)',
                      borderLeft: `3px solid ${sevColor}`,
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.8125rem', color: 'var(--text-primary)' }}>{risk.name}</span>
                        <span className={`risk-badge risk-${risk.severity.toLowerCase()}`}>{risk.severity}</span>
                      </div>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4, lineHeight: 1.5 }}>
                        {risk.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Model Insight + Benchmark */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              {outputs.model_explanation && (
                <div className="card" style={{ padding: 24 }}>
                  <h3 style={{ fontWeight: 600, marginBottom: 12, color: 'var(--text-primary)' }}>
                    <Info size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
                    AI Insights
                  </h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                    {outputs.model_explanation}
                  </p>
                </div>
              )}

              {outputs.benchmark_comparison && (
                <div className="card" style={{ padding: 24 }}>
                  <h3 style={{ fontWeight: 600, marginBottom: 12, color: 'var(--text-primary)' }}>
                    <TrendingUp size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
                    Benchmark
                  </h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                    {outputs.benchmark_comparison}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Input Summary */}
          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ fontWeight: 600, marginBottom: 12, color: 'var(--text-primary)' }}>
              <FileText size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
              Input Parameters
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
              {[
                { label: 'Project Type', value: inputs.project_type },
                { label: 'Team Size', value: inputs.team_size.toString() },
                { label: 'Duration', value: `${inputs.duration_months} months` },
                { label: 'Complexity', value: inputs.complexity },
                { label: 'Methodology', value: inputs.methodology },
                { label: 'Hourly Rate', value: `$${inputs.hourly_rate_usd}/hr` },
                { label: 'Tech Stack', value: inputs.tech_stack.join(', ') || 'Not specified' },
                { label: 'Features', value: inputs.feature_count ?? 'Not recorded' },
                { label: 'Integrations', value: inputs.integration_count ?? 'Not recorded' },
                { label: 'Requirements Volatility (1–5)', value: inputs.volatility_score ?? 'Not recorded' },
                { label: 'Team Experience (1–4)', value: inputs.team_experience ?? 'Not recorded' },
                { label: 'Function Points', value: inputs.size_fp ?? 'Not recorded' },
              ].map((item, i) => (
                <div key={i} style={{ padding: '8px 0' }}>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</p>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 500 }}>{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Model Transparency & Provenance Modal */}
          <ModelTransparencyModal
            isOpen={showTransparencyModal}
            onClose={() => setShowTransparencyModal(false)}
            modelVersion={model_version}
            tier={tier}
            sizeFp={inputs.size_fp}
            estimate={currentEstimate}
            currencyCode={useCurrencyStore.getState().currency}
            currencyRate={convert(1)}
          />
        </main>
      </div>
    </div>
  );
}
