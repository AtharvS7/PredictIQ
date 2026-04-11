import { Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import Navbar from '@/components/shared/Navbar';
import {
  Upload, Brain, DollarSign, Clock, Shield, FileText,
  ArrowRight, CheckCircle2, Zap, BarChart3, ChevronRight,
} from 'lucide-react';

const features = [
  { icon: Upload, title: 'Upload Any Doc', desc: 'PDF, DOCX, or TXT — drag and drop to start' },
  { icon: Brain, title: 'AI Extracts Scope', desc: 'NLP identifies tech stack, complexity, and timeline' },
  { icon: DollarSign, title: 'Cost Range', desc: 'Get min / likely / max cost with confidence interval' },
  { icon: Clock, title: 'Timeline Breakdown', desc: 'Phase-by-phase schedule with milestones' },
  { icon: Shield, title: 'Risk Analysis', desc: 'Top risk factors scored and prioritized' },
  { icon: FileText, title: 'Export & Share', desc: 'Branded PDF reports and shareable links' },
];

const steps = [
  { num: '01', title: 'Upload Document', desc: 'Drop your project spec, SRS, or proposal' },
  { num: '02', title: 'AI Analyzes Scope', desc: 'NLP + ML extracts parameters automatically' },
  { num: '03', title: 'Review Prediction', desc: 'See cost, timeline, risk, and phase breakdown' },
  { num: '04', title: 'Export & Share', desc: 'Download PDF or share a read-only link' },
];

export default function LandingPage() {
  const { session } = useAuthStore();

  return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />

      {/* ── Hero ──────────────────────────────────────────── */}
      <section style={{
        padding: '5rem 1.5rem 4rem',
        maxWidth: 1200, margin: '0 auto',
        textAlign: 'center',
      }}>
        <div className="animate-fade-in">
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '6px 16px', borderRadius: 999,
            background: 'rgba(26, 86, 219, 0.1)',
            color: 'var(--color-primary)', fontSize: '0.8125rem', fontWeight: 600,
            marginBottom: 24,
          }}>
            <Zap size={14} /> AI-Powered Estimation
          </div>

          <h1 style={{
            fontSize: 'clamp(2.25rem, 5vw, 3.75rem)',
            fontWeight: 800, lineHeight: 1.1,
            letterSpacing: '-0.03em',
            color: 'var(--text-primary)',
            marginBottom: 20, maxWidth: 800, margin: '0 auto 20px',
          }}>
            Predict Your Project Cost{' '}
            <span className="gradient-text">Before You Build</span>
          </h1>

          <p style={{
            fontSize: '1.125rem', color: 'var(--text-secondary)',
            maxWidth: 600, margin: '0 auto 32px', lineHeight: 1.7,
          }}>
            AI-powered cost and timeline estimation for software teams.
            Upload a project document and get a detailed prediction in seconds.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to={session ? '/estimate/new' : '/auth'} className="btn-primary" style={{
              padding: '14px 28px', fontSize: '1rem',
            }}>
              Get Started Free <ArrowRight size={18} />
            </Link>
            <a href="#how-it-works" className="btn-secondary" style={{
              padding: '14px 28px', fontSize: '1rem', textDecoration: 'none',
            }}>
              See How It Works
            </a>
          </div>
        </div>

        {/* Animated SVG Dashboard Preview */}
        <div style={{
          marginTop: 56, maxWidth: 900, margin: '56px auto 0',
          borderRadius: 16, overflow: 'hidden',
          border: '1px solid var(--border-color)',
          boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
          background: 'var(--bg-surface)',
          padding: 24,
        }}>
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16,
          }}>
            {[
              { label: 'Estimated Cost', value: '$285,000', color: '#1A56DB', sub: 'Most likely' },
              { label: 'Timeline', value: '22 weeks', color: '#10B981', sub: 'Optimistic' },
              { label: 'Risk Score', value: '42/100', color: '#F59E0B', sub: 'Medium' },
            ].map((card, i) => (
              <div key={i} style={{
                background: 'var(--bg-elevated)', borderRadius: 12,
                padding: 20, textAlign: 'left',
                animation: `fadeIn 0.5s ease ${i * 0.15}s both`,
              }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {card.label}
                </p>
                <p style={{ fontSize: '1.75rem', fontWeight: 700, color: card.color, marginTop: 4 }}>
                  {card.value}
                </p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                  {card.sub}
                </p>
              </div>
            ))}
          </div>
          <div style={{
            marginTop: 20, height: 120, borderRadius: 10,
            background: 'linear-gradient(135deg, rgba(26,86,219,0.05), rgba(16,185,129,0.05))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '1px dashed var(--border-color)',
          }}>
            <svg width="600" height="80" viewBox="0 0 600 80">
              <defs>
                <linearGradient id="chartGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#1A56DB" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#1A56DB" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path
                d="M0,60 Q100,20 200,45 T400,30 T600,50"
                fill="none" stroke="#1A56DB" strokeWidth="2"
                strokeDasharray="600" strokeDashoffset="600"
                style={{ animation: 'drawLine 2s ease forwards' }}
              />
              <path
                d="M0,60 Q100,20 200,45 T400,30 T600,50 L600,80 L0,80 Z"
                fill="url(#chartGrad)"
                opacity="0.3"
              />
            </svg>
          </div>
        </div>
        <style>{`
          @keyframes drawLine {
            to { stroke-dashoffset: 0; }
          }
        `}</style>
      </section>

      {/* ── Features Grid ────────────────────────────────── */}
      <section style={{
        padding: '4rem 1.5rem', maxWidth: 1200, margin: '0 auto',
      }}>
        <h2 style={{
          fontSize: '2rem', fontWeight: 700, textAlign: 'center',
          color: 'var(--text-primary)', marginBottom: 12,
        }}>
          Everything You Need to Estimate
        </h2>
        <p style={{
          textAlign: 'center', color: 'var(--text-secondary)',
          marginBottom: 48, fontSize: '1.0625rem',
        }}>
          From document upload to shareable reports — all powered by AI.
        </p>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 20,
        }}>
          {features.map(({ icon: Icon, title, desc }, i) => (
            <div key={i} className="card" style={{
              padding: 24, display: 'flex', gap: 16, alignItems: 'flex-start',
              animation: `fadeIn 0.4s ease ${i * 0.08}s both`,
            }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'rgba(26, 86, 219, 0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}>
                <Icon size={20} color="var(--color-primary)" />
              </div>
              <div>
                <h3 style={{ fontWeight: 600, fontSize: '0.9375rem', marginBottom: 4, color: 'var(--text-primary)' }}>
                  {title}
                </h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────── */}
      <section id="how-it-works" style={{
        padding: '4rem 1.5rem', maxWidth: 900, margin: '0 auto',
      }}>
        <h2 style={{
          fontSize: '2rem', fontWeight: 700, textAlign: 'center',
          color: 'var(--text-primary)', marginBottom: 48,
        }}>
          How It Works
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {steps.map(({ num, title, desc }, i) => (
            <div key={i} style={{
              display: 'flex', gap: 20, alignItems: 'flex-start', padding: '24px 0',
              borderBottom: i < steps.length - 1 ? '1px solid var(--border-color)' : 'none',
            }}>
              <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: 'var(--color-primary)', color: 'white',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, fontSize: '1rem', flexShrink: 0,
              }}>
                {num}
              </div>
              <div>
                <h3 style={{ fontWeight: 600, fontSize: '1.0625rem', color: 'var(--text-primary)', marginBottom: 4 }}>
                  {title}
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  {desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Social Proof ─────────────────────────────────── */}
      <section style={{
        padding: '4rem 1.5rem', maxWidth: 1200, margin: '0 auto',
      }}>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: 20,
        }}>
          {[
            { stat: '740+', label: 'Real projects in training data' },
            { stat: '4', label: 'International dataset sources' },
            { stat: '<30s', label: 'Per estimate generation' },
          ].map(({ stat, label }, i) => (
            <div key={i} style={{
              textAlign: 'center', padding: 32,
              background: 'var(--bg-surface)', borderRadius: 16,
              border: '1px solid var(--border-color)',
            }}>
              <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--color-primary)' }}>
                {stat}
              </p>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                {label}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────── */}
      <section style={{
        padding: '5rem 1.5rem', textAlign: 'center',
      }}>
        <h2 style={{
          fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16,
        }}>
          Ready to predict your next project?
        </h2>
        <Link to={session ? '/estimate/new' : '/auth'} className="btn-primary" style={{
          padding: '16px 32px', fontSize: '1.0625rem',
        }}>
          Start Estimating Now <ChevronRight size={18} />
        </Link>
      </section>

      {/* ── Footer ───────────────────────────────────────── */}
      <footer style={{
        borderTop: '1px solid var(--border-color)',
        padding: '2rem 1.5rem',
        textAlign: 'center',
        color: 'var(--text-tertiary)', fontSize: '0.8125rem',
      }}>
        <div style={{display: 'flex', justifyContent: 'center', gap: 24, marginBottom: 12}}>
          <span>Privacy Policy</span>
          <span>Terms</span>
          <span>API Docs</span>
          <span>Contact</span>
        </div>
        <p>© 2026 PredictIQ. Know Before You Build.</p>
      </footer>
    </div>
  );
}
