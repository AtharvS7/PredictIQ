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
import { exportPDF, duplicateEstimate, createShareLink } from '@/lib/api';
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
  BarChart3, PieChart, CircleDot, LineChart,
  HelpCircle,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { Badge, DataQualityBadge } from '@/components/shared/Badge';
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
  const [showTransparencyModal, setShowTransparencyModal] = useState(false);
  const [showMoreActions, setShowMoreActions] = useState(false);

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
                    className="cursor-pointer border-0 bg-transparent p-0 inline-flex items-center"
                    onClick={() => setShowTransparencyModal(true)}
                    title={`${tierInfo.name}: Click for estimate details`}
                    data-testid="tier-badge-transparency-trigger"
                  >
                    <DataQualityBadge tier={tier} showIcon />
                  </button>
                )}
              </div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {currentEstimate.project_name}
              </h1>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                {inputs.project_type} • Version {currentEstimate.version} • {new Date(currentEstimate.created_at).toLocaleDateString()}
              </p>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', position: 'relative' }}>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setShowTransparencyModal(true)}
                title="View details about this estimate"
                data-testid="how-it-works-button"
              >
                <HelpCircle size={15} className="text-blue-600 dark:text-blue-400" />
                <span>How this estimate works</span>
              </button>
              <CurrencySelector />
              <button className="btn-secondary" onClick={handleExportPDF}><Download size={15} /> PDF ({sym})</button>
              <button className="btn-secondary" onClick={handleExportJSON} data-testid="export-json-button"><FileDown size={15} /> JSON</button>
              <button className="btn-secondary" onClick={handleShare}><Share2 size={15} /> Share</button>
              <button className="btn-secondary" onClick={handleDuplicate}><Copy size={15} /> Duplicate</button>

              {/* More actions menu containing Copy JSON */}
              <div style={{ position: 'relative' }}>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowMoreActions((prev) => !prev)}
                  title="More actions"
                  aria-label="More actions"
                  style={{ minWidth: 36, padding: '6px 10px' }}
                >
                  &bull;&bull;&bull;
                </button>
                {showMoreActions && (
                  <div
                    style={{
                      position: 'absolute',
                      right: 0,
                      top: '100%',
                      marginTop: 4,
                      zIndex: 30,
                      background: 'var(--bg-surface)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 8,
                      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      padding: '4px 0',
                      minWidth: 140,
                    }}
                    onMouseLeave={() => setShowMoreActions(false)}
                  >
                    <button
                      type="button"
                      onClick={() => {
                        handleCopyJSON();
                        setShowMoreActions(false);
                      }}
                      className="btn-secondary"
                      data-testid="copy-json-button"
                      style={{
                        width: '100%',
                        border: 'none',
                        borderRadius: 0,
                        justifyContent: 'flex-start',
                        padding: '8px 12px',
                        background: 'transparent',
                        fontSize: '0.75rem',
                      }}
                    >
                      <Copy size={14} className="text-blue-600 dark:text-blue-400" />
                      <span>Copy JSON</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Out of Distribution (OOD) Guidance & Explanations */}
          <OODDiagnosticsCard inputs={inputs} reasons={oodStatus.reasons} className="mb-5" />

          {/* Hero Card: Likely Effort, Person-Months & Cost */}
          <Card variant="elevated" padding="lg" className="mb-5 border-t-4 border-t-blue-600 dark:border-t-blue-500 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle as="h3" className="text-lg font-bold flex items-center gap-2">
                <span>Likely effort</span>
              </CardTitle>
              <CardDescription className="text-sm text-[var(--text-secondary)]">
                Most likely delivery effort based on your functional scope
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-2">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))', gap: 16 }}>
                {/* Optimistic */}
                <div className="card" style={{ padding: 20, textAlign: 'center', background: 'var(--bg-elevated)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                  <p style={{ fontSize: '0.6875rem', color: '#10B981', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Optimistic (P10)
                  </p>
                  <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: 4 }}>
                    {outputs.effort_min_hours.toLocaleString()} hrs
                  </p>
                  <p style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 600, marginTop: 2 }}>
                    {p10PM.formatted}
                  </p>
                  <p
                    style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: 4, cursor: 'help' }}
                    title={`$${Math.round(outputs.cost_min_usd).toLocaleString('en-US')} USD`}
                  >
                    {format(outputs.cost_min_usd)}
                  </p>
                </div>

                {/* Most Likely (P50) */}
                <div className="card" style={{ padding: 20, textAlign: 'center', background: 'var(--bg-elevated)', border: '2px solid #2563EB', boxShadow: '0 2px 8px rgba(37,99,235,0.15)' }}>
                  <p style={{ fontSize: '0.6875rem', color: '#2563EB', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Most Likely (P50)
                  </p>
                  <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-primary)', marginTop: 4 }}>
                    {outputs.effort_likely_hours.toLocaleString()} hrs
                  </p>
                  <p style={{ fontSize: '0.8125rem', color: '#2563EB', fontWeight: 700, marginTop: 2 }}>
                    {p50PM.formatted}
                  </p>
                  <p
                    style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 700, marginTop: 4, cursor: 'help' }}
                    title={`$${Math.round(outputs.cost_likely_usd).toLocaleString('en-US')} USD`}
                  >
                    {format(outputs.cost_likely_usd)}
                    <span style={{ fontSize: '0.75rem', fontWeight: 400, color: 'var(--text-secondary)', marginLeft: 6 }}>
                      (at {sym}{Math.round(inputs.hourly_rate_usd * convert(1)).toLocaleString()}/hour)
                    </span>
                  </p>
                </div>

                {/* Conservative */}
                <div className="card" style={{ padding: 20, textAlign: 'center', background: 'var(--bg-elevated)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                  <p style={{ fontSize: '0.6875rem', color: '#F59E0B', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Conservative (P90)
                  </p>
                  <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: 4 }}>
                    {outputs.effort_max_hours.toLocaleString()} hrs
                  </p>
                  <p style={{ fontSize: '0.75rem', color: '#F59E0B', fontWeight: 600, marginTop: 2 }}>
                    {p90PM.formatted}
                  </p>
                  <p
                    style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: 4, cursor: 'help' }}
                    title={`$${Math.round(outputs.cost_max_usd).toLocaleString('en-US')} USD`}
                  >
                    {format(outputs.cost_max_usd)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Effort Ranges Card */}
          <Card variant="elevated" padding="lg" className="mb-5 border-t-4 border-t-[var(--color-primary)]">
            <CardHeader className="pb-2">
              <CardTitle as="h3" className="text-lg font-bold flex items-center gap-2">
                <span>Effort ranges</span>
              </CardTitle>
              <CardDescription className="text-xs text-[var(--text-secondary)]">
                Likely range (middle half of outcomes) and plausible range (almost all outcomes)
              </CardDescription>
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
                ariaLabel="Effort ranges"
              />
            </CardContent>
          </Card>

          {/* Three Summary Tiles: Timeline, Cost Range, Risk */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))', gap: 16, marginBottom: 20 }}>
            {/* Timeline */}
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <Clock size={20} color="#10B981" />
              <p style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginTop: 6 }}>
                Project Timeline
              </p>
              <p style={{ fontSize: '1.75rem', fontWeight: 700, color: '#10B981', marginTop: 4 }}>
                {outputs.timeline_likely_weeks.toFixed(0)} wks
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                {outputs.timeline_min_weeks.toFixed(0)}–{outputs.timeline_max_weeks.toFixed(0)} wks range
              </p>
            </div>

            {/* Cost Range */}
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <TrendingUp size={20} color="var(--color-primary)" />
              <p style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginTop: 6 }}>
                Cost Range
              </p>
              <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)', marginTop: 4 }}>
                {format(outputs.cost_min_usd)} – {format(outputs.cost_max_usd)}
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                at {sym}{Math.round(inputs.hourly_rate_usd * convert(1)).toLocaleString()}/hour
              </p>
            </div>

            {/* Risk Score */}
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <Shield size={20} color={riskColor} />
              <p style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginTop: 6 }}>
                Risk Profile
              </p>
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
            <div className="table-scroll-container" style={{ marginTop: 16, overflowX: 'auto' }}>
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
                    Industry Context
                  </h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                    {outputs.benchmark_comparison}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Input Summary */}
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontWeight: 600, marginBottom: 4, color: 'var(--text-primary)' }}>
              <FileText size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
              Input Parameters
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: 14 }}>
              Persisted project inputs.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 16 }}>
              {[
                { label: 'Project Type', value: inputs.project_type },
                { label: 'Team Size', value: inputs.team_size.toString() },
                { label: 'Duration', value: `${inputs.duration_months} months` },
                { label: 'Complexity', value: inputs.complexity },
                { label: 'Delivery Process', value: inputs.methodology },
                { label: 'Hourly Rate', value: `$${inputs.hourly_rate_usd}/hr` },
                { label: 'Features', value: inputs.feature_count ?? 'Not recorded' },
                { label: 'Integrations', value: inputs.integration_count ?? 'Not recorded' },
                { label: 'Requirements Volatility (1–5)', value: inputs.volatility_score ?? 'Not recorded' },
                { label: 'Team Experience (1–4)', value: inputs.team_experience ?? 'Not recorded' },
                { label: 'Function Points', value: currentEstimate.size?.value ?? inputs.size_fp ?? 'Not recorded' },
              ].map((item, i) => (
                <div key={i} style={{ padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</p>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 500 }}>{item.value}</p>
                </div>
              ))}
            </div>

            {/* Tech Stack Chips Container */}
            <div style={{ padding: '12px 14px', background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
              <p style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                Technology Stack
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {inputs.tech_stack && inputs.tech_stack.length > 0 ? (
                  inputs.tech_stack.map((tech, idx) => (
                    <span
                      key={idx}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 6,
                        fontSize: '0.75rem',
                        fontWeight: 500,
                        background: 'var(--bg-surface)',
                        color: 'var(--text-primary)',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      {tech}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Not specified</span>
                )}
              </div>
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
