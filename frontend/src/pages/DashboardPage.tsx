import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import { useAuthStore } from '@/store/authStore';
import { useEstimateStore } from '@/store/estimateStore';
import { FileText, Target, Calendar, PlusCircle, ArrowRight, Upload } from 'lucide-react';

export default function DashboardPage() {
  const { profile } = useAuthStore();
  const { estimates, totalEstimates, loading, fetchEstimates } = useEstimateStore();
  const navigate = useNavigate();

  useEffect(() => { fetchEstimates(); }, [fetchEstimates]);

  const firstName = profile?.full_name?.split(' ')[0] || 'there';
  const avgConfidence = estimates.length > 0
    ? (estimates.reduce((sum, e) => sum + (e.confidence_pct || 0), 0) / estimates.length).toFixed(0)
    : '—';
  const thisMonth = estimates.filter((e) => {
    const d = new Date(e.created_at);
    const now = new Date();
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  }).length;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: 1100 }}>
          {/* Welcome Banner */}
          <div className="animate-fade-in" style={{
            marginBottom: 32,
            background: 'linear-gradient(135deg, #1A56DB, #3B82F6)',
            borderRadius: 16, padding: '28px 32px', color: 'white',
          }}>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 4 }}>
              Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 17 ? 'afternoon' : 'evening'}, {firstName}!
            </h1>
            <p style={{ opacity: 0.85, fontSize: '0.9375rem' }}>
              Ready to estimate? Upload a document or start a manual estimate.
            </p>
            <Link to="/estimate/new" className="btn-secondary" style={{
              marginTop: 16, background: 'white', color: '#1A56DB', borderColor: 'transparent',
              fontWeight: 600,
            }}>
              <PlusCircle size={16} /> New Estimate
            </Link>
          </div>

          {/* Quick Stats */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 16, marginBottom: 32,
          }}>
            {[
              { icon: FileText, label: 'Total Estimates', value: totalEstimates.toString(), color: '#1A56DB' },
              { icon: Target, label: 'Avg Confidence', value: `${avgConfidence}%`, color: '#10B981' },
              { icon: Calendar, label: 'This Month', value: thisMonth.toString(), color: '#F59E0B' },
            ].map(({ icon: Icon, label, value, color }, i) => (
              <div key={i} className="card" style={{ padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 10,
                    background: `${color}15`, display: 'flex',
                    alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Icon size={20} color={color} />
                  </div>
                  <div>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</p>
                    <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>{value}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Upload & Recent */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            {/* Quick Upload */}
            <div className="card" style={{ padding: 24 }}>
              <h3 style={{ fontWeight: 600, marginBottom: 16, color: 'var(--text-primary)' }}>Quick Upload</h3>
              <Link to="/estimate/new" style={{ textDecoration: 'none' }}>
                <div style={{
                  border: '2px dashed var(--border-color)', borderRadius: 12,
                  padding: 32, textAlign: 'center',
                  cursor: 'pointer', transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.background = 'rgba(26,86,219,0.03)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-color)'; e.currentTarget.style.background = 'transparent'; }}
                >
                  <Upload size={32} color="var(--text-tertiary)" style={{ margin: '0 auto 12px' }} />
                  <p style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: '0.9375rem' }}>
                    Drop a project document
                  </p>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                    PDF, DOCX, or TXT • Max 10MB
                  </p>
                </div>
              </Link>
            </div>

            {/* Recent Estimates */}
            <div className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Recent Estimates</h3>
                <Link to="/estimates" style={{ fontSize: '0.8125rem', color: 'var(--color-primary)', textDecoration: 'none', fontWeight: 500 }}>
                  View all <ArrowRight size={13} style={{ verticalAlign: 'middle' }} />
                </Link>
              </div>

              {loading ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="skeleton" style={{ height: 52, borderRadius: 10 }} />
                  ))}
                </div>
              ) : estimates.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 32, color: 'var(--text-tertiary)' }}>
                  <FileText size={32} style={{ marginBottom: 8, opacity: 0.5 }} />
                  <p style={{ fontSize: '0.875rem' }}>No estimates yet.</p>
                  <Link to="/estimate/new" style={{ fontSize: '0.8125rem', color: 'var(--color-primary)', textDecoration: 'none', fontWeight: 500 }}>
                    Create your first estimate
                  </Link>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {estimates.slice(0, 5).map((est) => (
                    <div
                      key={est.id}
                      onClick={() => navigate(`/estimate/${est.id}/results`)}
                      style={{
                        padding: '10px 12px', borderRadius: 10,
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        cursor: 'pointer', transition: 'background 0.15s',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-elevated)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <div>
                        <p style={{ fontWeight: 500, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                          {est.project_name}
                        </p>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                          {est.project_type} • v{est.version}
                        </p>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <p style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-primary)' }}>
                          ${est.cost_likely_usd?.toLocaleString() ?? '—'}
                        </p>
                        <span className={`risk-badge risk-${est.risk_level?.toLowerCase()}`}>
                          {est.risk_level}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
