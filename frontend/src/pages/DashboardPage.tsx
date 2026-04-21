import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import { useAuthStore } from '@/store/authStore';
import { useEstimateStore } from '@/store/estimateStore';
import {
  FileText,
  Target,
  Calendar,
  PlusCircle,
  ArrowRight,
  Upload
} from 'lucide-react';

export default function DashboardPage() {
  const { profile } = useAuthStore();
  const { estimates, totalEstimates, loading, fetchEstimates } =
    useEstimateStore();

  const navigate = useNavigate();

  // Sidebar state
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    fetchEstimates();
  }, [fetchEstimates]);

  const firstName =
    profile?.full_name?.split(' ')[0] || 'there';

  const avgConfidence =
    estimates.length > 0
      ? (
        estimates.reduce(
          (sum, e) => sum + (e.confidence_pct || 0),
          0
        ) / estimates.length
      ).toFixed(0)
      : '—';

  const thisMonth = estimates.filter((e) => {
    const d = new Date(e.created_at);
    const now = new Date();

    return (
      d.getMonth() === now.getMonth() &&
      d.getFullYear() === now.getFullYear()
    );
  }).length;

  const getRiskColor = (risk?: string) => {
    if (!risk) return 'black';

    switch (risk.toLowerCase()) {
      case 'low':
        return '#DC2626';
      case 'medium':
        return '#1E3A8A';
      case 'high':
        return '#16A34A';
      default:
        return 'black';
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <div style={{ display: 'flex' }}>
        {/* Sidebar */}
        <Sidebar
          collapsed={collapsed}
          setCollapsed={setCollapsed}
        />

        {/* Main Content */}
        <main
          style={{
            flex: 1,
            padding: '2rem',

            display: 'flex',
            justifyContent: 'center', // always center
            transition: 'all 0.25s ease'
          }}
        >
          {/* CENTER CONTAINER */}
          <div
            style={{
              width: '100%',
              maxWidth: 1100,
              margin: '0 auto'
            }}
          >
            {/* WELCOME */}
            <div
              style={{
                marginBottom: 32,
                border: `2px solid var(--text-primary)`,
                borderRadius: 16,
                padding: '28px 32px',
                background: 'transparent'
              }}
            >
              <h1
                style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  marginBottom: 4,
                  color: 'var(--text-primary)'
                }}
              >
                Good{' '}
                {new Date().getHours() < 12
                  ? 'morning'
                  : new Date().getHours() < 17
                    ? 'afternoon'
                    : 'evening'}
                , {firstName}!
              </h1>

              <p
                style={{
                  color: 'var(--text-primary)',
                  fontSize: '0.9375rem'
                }}
              >
                Ready to estimate? Upload a document or start a manual estimate.
              </p>

              <Link
                to="/estimate/new"
                style={{
                  marginTop: 16,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'transparent',
                  border: `2px solid var(--text-primary)`,
                  color: 'var(--text-primary)',
                  fontWeight: 600,
                  padding: '10px 16px',
                  borderRadius: 8,
                  textDecoration: 'none'
                }}
              >
                <PlusCircle size={16} />
                New Estimate
              </Link>
            </div>

            {/* STATS */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns:
                  'repeat(auto-fit, minmax(220px, 1fr))',
                gap: 16,
                marginBottom: 32
              }}
            >
              {[
                {
                  icon: FileText,
                  label: 'Total Estimates',
                  value: totalEstimates.toString()
                },
                {
                  icon: Target,
                  label: 'Avg Confidence',
                  value: `${avgConfidence}%`
                },
                {
                  icon: Calendar,
                  label: 'This Month',
                  value: thisMonth.toString()
                }
              ].map(({ icon: Icon, label, value }, i) => (
                <div key={i} className="card" style={{ padding: 20 }}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12
                    }}
                  >
                    <Icon size={20} color="var(--text-primary)" />

                    <div>
                      <p
                        style={{
                          fontSize: '0.75rem',
                          color: 'var(--text-primary)'
                        }}
                      >
                        {label}
                      </p>

                      <p
                        style={{
                          fontSize: '1.5rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)'
                        }}
                      >
                        {value}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* QUICK + RECENT */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: 20
              }}
            >
              {/* QUICK UPLOAD */}
              <div className="card" style={{ padding: 24 }}>
                <h3 style={{ fontWeight: 600, marginBottom: 16 }}>
                  Quick Upload
                </h3>

                <Link
                  to="/estimate/new"
                  style={{ textDecoration: 'none' }}
                >
                  <div
                    style={{
                      border: `2px dashed var(--text-primary)`,
                      borderRadius: 12,
                      padding: 32,
                      textAlign: 'center'
                    }}
                  >
                    <Upload size={32} color="var(--text-primary)" />

                    <p
                      style={{
                        fontWeight: 500,
                        color: 'var(--text-primary)'
                      }}
                    >
                      Drop a project document
                    </p>

                    <p
                      style={{
                        fontSize: '0.8125rem',
                        color: 'var(--text-primary)'
                      }}
                    >
                      PDF, DOCX, or TXT • Max 10MB
                    </p>
                  </div>
                </Link>
              </div>

              {/* RECENT */}
              <div className="card" style={{ padding: 24 }}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: 16
                  }}
                >
                  <h3 style={{ fontWeight: 600 }}>
                    Recent Estimates
                  </h3>

                  <Link to="/estimates">
                    View all <ArrowRight size={13} />
                  </Link>
                </div>

                {loading ? (
                  <div>Loading...</div>
                ) : estimates.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: 32 }}>
                    <FileText size={32} />
                    <p>No estimates yet.</p>
                  </div>
                ) : (
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 8
                    }}
                  >
                    {estimates.slice(0, 5).map((est) => (
                      <div
                        key={est.id}
                        onClick={() =>
                          navigate(
                            `/estimate/${est.id}/results`
                          )
                        }
                        style={{
                          padding: '10px 12px',
                          borderRadius: 10,
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          cursor: 'pointer'
                        }}
                      >
                        <div>
                          <p style={{ fontWeight: 500 }}>
                            {est.project_name}
                          </p>

                          <p style={{ fontSize: '0.75rem' }}>
                            {est.project_type} • v{est.version}
                          </p>
                        </div>

                        <div style={{ textAlign: 'right' }}>
                          <p
                            style={{
                              fontWeight: 600,
                              color: getRiskColor(
                                est.risk_level
                              )
                            }}
                          >
                            $
                            {est.cost_likely_usd?.toLocaleString() ??
                              '—'}
                          </p>

                          <span
                            style={{
                              padding: '4px 8px',
                              borderRadius: 6,
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              color: 'white',
                              backgroundColor: getRiskColor(
                                est.risk_level
                              )
                            }}
                          >
                            {est.risk_level}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}