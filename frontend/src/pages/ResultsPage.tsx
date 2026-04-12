import { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import CurrencySelector from '@/components/shared/CurrencySelector';
import { useEstimateStore } from '@/store/estimateStore';
import { useCurrencyStore } from '@/store/currencyStore';
import { useToast } from '@/App';
import { exportPDF, duplicateEstimate, createShareLink } from '@/lib/api';
import {
  BarChart as RechartsBarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import {
  Download, Copy, Share2, Edit3, ArrowLeft, Clock, DollarSign,
  Shield, TrendingUp, AlertTriangle, Info, FileText,
} from 'lucide-react';

const PHASE_COLORS = ['#1A56DB', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const { currentEstimate, loading, fetchEstimate } = useEstimateStore();
  const { format, convert, symbol } = useCurrencyStore();
  const sym = symbol();
  const { addToast } = useToast();

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
    Low: '#10B981', Medium: '#3B82F6', High: '#F59E0B', Critical: '#EF4444',
  }[outputs.risk_level] || '#64748B';


  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: 1100 }}>
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
            <h3 style={{ fontWeight: 600, marginBottom: 16, color: 'var(--text-primary)' }}>
              <TrendingUp size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
              Phase Breakdown
            </h3>
            <div style={{ height: 260 }}>
              <ResponsiveContainer>
                <RechartsBarChart data={phaseData} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" tickFormatter={(v: number) => `${sym}${(v/1000).toFixed(0)}k`} />
                  <YAxis type="category" dataKey="name" width={100} fontSize={12} />
                  <Tooltip
                    formatter={(val: unknown) => [format(Number(val) / (convert(1))), 'Cost']}
                    labelFormatter={(label: any) => phaseData.find(p => p.name === label)?.fullName || String(label)}
                    contentStyle={{
                      background: 'var(--bg-surface)', border: '1px solid var(--border-color)',
                      borderRadius: 10, fontSize: '0.8125rem',
                    }}
                  />
                  <Bar dataKey="cost" radius={[0, 6, 6, 0]}>
                    {phaseData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </RechartsBarChart>
              </ResponsiveContainer>
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
                    Low: '#10B981', Medium: '#3B82F6', High: '#F59E0B', Critical: '#EF4444',
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
