import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import CurrencySelector from '@/components/shared/CurrencySelector';
import { useEstimateStore } from '@/store/estimateStore';
import { useCurrencyStore } from '@/store/currencyStore';
import { useToast } from '@/App';
import { exportPDF, duplicateEstimate, createShareLink } from '@/lib/api';
import { Bar, PolarArea, Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  RadialLinearScale, ArcElement, PointElement, LineElement, Filler,
  Tooltip as ChartTooltip, Legend,
} from 'chart.js';
import {
  Download, Copy, Share2, ArrowLeft, Clock,
  Shield, TrendingUp, AlertTriangle, Info, FileText,
  BarChart3, PieChart, CircleDot, LineChart,
} from 'lucide-react';

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
  const { id } = useParams<{ id: string }>();
  const { currentEstimate, loading, fetchEstimate } = useEstimateStore();
  const { format, convert, symbol } = useCurrencyStore();
  const sym = symbol();
  const { addToast } = useToast();
  const [chartType, setChartType] = useState<ChartType>('bar');

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
      addToast('success', 'PDF exported!');
    } catch {
      addToast('error', 'PDF export failed');
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
      navigator.clipboard.writeText(window.location.origin + data.share_url);
      addToast('success', 'Share link copied to clipboard!');
    } catch {
      addToast('error', 'Failed to create share link');
    }
  };

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

  const { inputs, outputs } = currentEstimate;
  const phaseData = outputs.phase_breakdown.map((p, i) => ({
    name: p.phase.replace('& ', '').split(' ')[0],
    fullName: p.phase,
    hours: p.effort_hours,
    cost: convert(p.cost_usd),
    pct: p.pct_of_total,
    fill: PHASE_COLORS[i % PHASE_COLORS.length],
  }));

  const riskColor = {
    Low: '#EF4444', Medium: '#3B82F6', High: '#10B981', Critical: '#EF4444',
  }[outputs.risk_level] || '#64748B';

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
      label: (ctx: any) => `Cost: ${format(ctx.raw / convert(1))}`,
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
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {currentEstimate.project_name}
              </h1>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                {inputs.project_type} • v{currentEstimate.version} •
                {new Date(currentEstimate.created_at).toLocaleDateString()}
              </p>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <CurrencySelector />
              <button className="btn-secondary" onClick={handleExportPDF}><Download size={15} /> PDF ({sym})</button>
              <button className="btn-secondary" onClick={handleShare}><Share2 size={15} /> Share</button>
              <button className="btn-secondary" onClick={handleDuplicate}><Copy size={15} /> Duplicate</button>
            </div>
          </div>

          {/* Cost Summary */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
            {[
              { label: 'Optimistic', value: outputs.cost_min_usd, color: '#10B981', sub: `${outputs.effort_min_hours.toLocaleString()} hrs` },
              { label: 'Most Likely', value: outputs.cost_likely_usd, color: '#1A56DB', sub: `${outputs.effort_likely_hours.toLocaleString()} hrs`, primary: true },
              { label: 'Conservative', value: outputs.cost_max_usd, color: '#F59E0B', sub: `${outputs.effort_max_hours.toLocaleString()} hrs` },
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
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
            {/* Confidence */}
            <div className="card" style={{ padding: 20, textAlign: 'center' }}>
              <TrendingUp size={20} color="var(--color-primary)" />
              <p style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)', marginTop: 4 }}>
                {outputs.confidence_pct.toFixed(0)}%
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Confidence</p>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                <TrendingUp size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
                Phase Breakdown
              </h3>
              {/* Chart Type Switcher */}
              <div style={{
                display: 'flex', gap: 4,
                background: 'var(--bg-elevated)', borderRadius: 10, padding: 3,
              }}>
                {chartOptions.map(opt => (
                  <button
                    key={opt.key}
                    onClick={() => setChartType(opt.key)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 4,
                      padding: '6px 12px', borderRadius: 8, border: 'none',
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
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
            {/* Risks */}
            <div className="card" style={{ padding: 24 }}>
              <h3 style={{ fontWeight: 600, marginBottom: 16, color: 'var(--text-primary)' }}>
                <AlertTriangle size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
                Top Risk Factors
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {outputs.top_risks.map((risk, i) => {
                  const sevColor = {
                    Low: '#EF4444', Medium: '#3B82F6', High: '#10B981', Critical: '#EF4444',
                  }[risk.severity];
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
              ].map((item, i) => (
                <div key={i} style={{ padding: '8px 0' }}>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</p>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 500 }}>{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
