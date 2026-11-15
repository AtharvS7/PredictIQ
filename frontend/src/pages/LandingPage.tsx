import { Link, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import Navbar from '@/components/shared/Navbar';
import SEOHead from '@/components/shared/SEOHead';
import {
  ArrowRight,
  ChevronRight,
  FileText,
  BarChart3,
  DollarSign,
  ShieldCheck,
  Users,
  Download,
} from 'lucide-react';

const steps = [
  {
    num: '01',
    title: 'Define Scope & Functional Size',
    desc: 'Enter functional scope directly or upload a requirements specification document (PDF, Word, Markdown, or text).',
  },
  {
    num: '02',
    title: 'Configure Team & Project Parameters',
    desc: 'Specify project duration, team composition, hourly billing rates, and organizational parameters.',
  },
  {
    num: '03',
    title: 'Obtain Calibrated Effort & Budget Bounds',
    desc: 'Receive empirical effort distributions, multi-currency budget forecasts, and exportable executive reports.',
  },
];

const features = [
  {
    icon: <BarChart3 size={24} style={{ color: 'var(--color-primary)' }} />,
    title: 'Empirical Benchmark Calibration',
    desc: 'Estimates calibrated on real-world historical engineering records to eliminate subjective planning bias.',
  },
  {
    icon: <ShieldCheck size={24} style={{ color: 'var(--color-primary)' }} />,
    title: 'Calibrated Confidence Intervals',
    desc: 'Clear likely and plausible uncertainty intervals that enable realistic contingency planning and stakeholder transparency.',
  },
  {
    icon: <FileText size={24} style={{ color: 'var(--color-primary)' }} />,
    title: 'Automated Document Analysis',
    desc: 'Intelligent natural language parser extracts functional modules, complexity, and scope directly from specification files.',
  },
  {
    icon: <DollarSign size={24} style={{ color: 'var(--color-primary)' }} />,
    title: 'Multi-Currency Budget Planner',
    desc: 'Dynamic scenario modeling across international currencies with automated exchange rate conversion.',
  },
  {
    icon: <Users size={24} style={{ color: 'var(--color-primary)' }} />,
    title: 'Team Composition & Staffing',
    desc: 'Analyze resource allocation, staffing curves, and monthly run rates across project delivery phases.',
  },
  {
    icon: <Download size={24} style={{ color: 'var(--color-primary)' }} />,
    title: 'Executive Export Reports',
    desc: 'Generate comprehensive estimation dossiers in PDF, CSV, and structured JSON formats for leadership review.',
  },
];

export default function LandingPage() {
  const { user } = useAuthStore();

  // Redirect authenticated users directly to their dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <SEOHead
        title="Software Effort & Cost Estimation"
        description="PredictIQ provides empirical software effort estimation, project budget planning, and requirements document analysis."
      />
      <Navbar />

      {/* HERO SECTION */}
      <section
        className="gradient-mesh"
        style={{
          padding: '4.5rem 1.5rem 3.5rem',
          maxWidth: 1200,
          margin: '0 auto',
          textAlign: 'center',
          width: '100%',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '6px 16px',
            borderRadius: 20,
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-color)',
            fontSize: '0.875rem',
            fontWeight: 500,
            color: 'var(--text-secondary)',
            marginBottom: 24,
          }}
        >
          <span>Empirical Software Project Intelligence</span>
        </div>

        <h1
          style={{
            fontSize: 'clamp(2.25rem, 5vw, 3.5rem)',
            fontWeight: 800,
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            color: 'var(--text-primary)',
            maxWidth: 860,
            margin: '0 auto 20px',
          }}
        >
          Plan Software Project Budgets{' '}
          <span style={{ color: 'var(--color-primary)' }}>
            With Calibrated Confidence
          </span>
        </h1>

        <p
          style={{
            fontSize: '1.125rem',
            color: 'var(--text-secondary)',
            maxWidth: 680,
            margin: '0 auto 36px',
            lineHeight: 1.7,
          }}
        >
          PredictIQ combines empirical engineering benchmarks with automated document
          analysis to deliver transparent effort forecasts, realistic delivery timelines,
          and reliable cost bounds before you build.
        </p>

        {/* HERO ACTIONS */}
        <div
          style={{
            display: 'flex',
            gap: 14,
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          <Link
            to="/auth?mode=register"
            style={{
              padding: '14px 28px',
              fontSize: '1rem',
              textDecoration: 'none',
              background: 'var(--color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 10,
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              transition: 'opacity 0.2s ease',
              cursor: 'pointer',
            }}
          >
            Create Free Account
            <ArrowRight size={18} />
          </Link>

          <Link
            to="/auth?mode=login"
            style={{
              padding: '14px 28px',
              fontSize: '1rem',
              textDecoration: 'none',
              background: 'var(--bg-surface)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: 10,
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              transition: 'all 0.2s ease',
              cursor: 'pointer',
            }}
          >
            Sign In
          </Link>

          <a
            href="#how-it-works"
            style={{
              padding: '14px 24px',
              fontSize: '1rem',
              textDecoration: 'none',
              background: 'transparent',
              color: 'var(--text-secondary)',
              borderRadius: 10,
              fontWeight: 500,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            How It Works
          </a>
        </div>
      </section>

      {/* 3-STEP PROCESS SECTION */}
      <section
        id="how-it-works"
        style={{
          padding: '4rem 1.5rem',
          maxWidth: 1000,
          margin: '0 auto',
          width: '100%',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <h2
            style={{
              fontSize: '2rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 12,
            }}
          >
            Three Steps to Calibrated Estimates
          </h2>
          <p
            style={{
              fontSize: '1rem',
              color: 'var(--text-secondary)',
              maxWidth: 580,
              margin: '0 auto',
            }}
          >
            Transform ambiguous project specifications into auditable effort distributions and budget models.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {steps.map(({ num, title, desc }) => (
            <div
              key={num}
              style={{
                display: 'flex',
                gap: 20,
                alignItems: 'flex-start',
                padding: '24px',
                background: 'var(--bg-surface)',
                borderRadius: 14,
                border: '1px solid var(--border-color)',
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 12,
                  background: 'var(--color-primary)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '1.125rem',
                  flexShrink: 0,
                }}
              >
                {num}
              </div>

              <div>
                <h3
                  style={{
                    fontWeight: 600,
                    fontSize: '1.125rem',
                    color: 'var(--text-primary)',
                    marginBottom: 6,
                  }}
                >
                  {title}
                </h3>
                <p
                  style={{
                    fontSize: '0.9375rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.6,
                    margin: 0,
                  }}
                >
                  {desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURE HIGHLIGHTS GRID */}
      <section
        style={{
          padding: '4rem 1.5rem',
          background: 'var(--bg-secondary)',
          width: '100%',
        }}
      >
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2
              style={{
                fontSize: '2rem',
                fontWeight: 700,
                color: 'var(--text-primary)',
                marginBottom: 12,
              }}
            >
              Enterprise Estimation Capabilities
            </h2>
            <p
              style={{
                fontSize: '1rem',
                color: 'var(--text-secondary)',
                maxWidth: 620,
                margin: '0 auto',
              }}
            >
              Everything engineering directors, delivery leads, and project managers need to plan software initiatives accurately.
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: 24,
            }}
          >
            {features.map((feat, idx) => (
              <div
                key={idx}
                style={{
                  padding: '28px',
                  background: 'var(--bg-surface)',
                  borderRadius: 14,
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 14,
                }}
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 10,
                    background: 'var(--bg-elevated)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {feat.icon}
                </div>
                <h3
                  style={{
                    fontSize: '1.125rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    margin: 0,
                  }}
                >
                  {feat.title}
                </h3>
                <p
                  style={{
                    fontSize: '0.875rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.6,
                    margin: 0,
                  }}
                >
                  {feat.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CALL TO ACTION */}
      <section
        style={{
          padding: '5rem 1.5rem',
          textAlign: 'center',
          maxWidth: 800,
          margin: '0 auto',
          width: '100%',
        }}
      >
        <h2
          style={{
            fontSize: '2.25rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            marginBottom: 16,
          }}
        >
          Ready to plan your next engineering initiative?
        </h2>
        <p
          style={{
            fontSize: '1.0625rem',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            marginBottom: 32,
          }}
        >
          Join engineering teams using PredictIQ to size requirements, forecast delivery dates,
          and secure stakeholder alignment with calibrated evidence.
        </p>

        <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link
            to="/auth?mode=register"
            style={{
              padding: '16px 32px',
              fontSize: '1.0625rem',
              background: 'var(--color-primary)',
              color: 'white',
              borderRadius: 10,
              textDecoration: 'none',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Create Your Account
            <ChevronRight size={18} />
          </Link>
          <Link
            to="/auth?mode=login"
            style={{
              padding: '16px 28px',
              fontSize: '1.0625rem',
              background: 'var(--bg-surface)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: 10,
              textDecoration: 'none',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              cursor: 'pointer',
            }}
          >
            Sign In
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer
        style={{
          borderTop: '1px solid var(--border-color)',
          padding: '2.5rem 1.5rem',
          textAlign: 'center',
          color: 'var(--text-tertiary)',
          fontSize: '0.875rem',
          marginTop: 'auto',
          background: 'var(--bg-surface)',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: 24,
            marginBottom: 16,
            color: 'var(--text-secondary)',
            flexWrap: 'wrap',
          }}
        >
          <span style={{ cursor: 'pointer' }}>Privacy Policy</span>
          <span style={{ cursor: 'pointer' }}>Terms of Service</span>
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            style={{ color: 'inherit', textDecoration: 'none' }}
          >
            API Documentation
          </a>
          <span style={{ cursor: 'pointer' }}>Contact Support</span>
        </div>

        <p
          style={{
            color: 'var(--text-tertiary)',
            margin: 0,
            fontSize: '0.8125rem',
          }}
        >
          © 2026 PredictIQ. Calibrated Software Engineering Intelligence.
        </p>
      </footer>
    </div>
  );
}
