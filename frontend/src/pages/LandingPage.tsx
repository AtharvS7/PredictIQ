import { Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import Navbar from '@/components/shared/Navbar';
import {
  Upload,
  Brain,
  DollarSign,
  Clock,
  Shield,
  FileText,
  ArrowRight,
  ChevronRight,
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

      {/* HERO SECTION */}
      <section
        className="gradient-mesh"
        style={{
          padding: '5rem 1.5rem 4rem',
          maxWidth: 1200,
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            fontSize: 'clamp(2.25rem, 5vw, 3.75rem)',
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            color: 'var(--text-primary)',
            maxWidth: 800,
            margin: '0 auto 20px',
            textAlign: 'center',
          }}
        >
          Predict Your Project Cost{' '}
          <span style={{ color: 'var(--text-primary)' }}>
            Before You Build
          </span>
        </h1>

        <p
          style={{
            fontSize: '1.125rem',
            color: 'var(--text-secondary)',
            maxWidth: 600,
            margin: '0 auto 32px',
            lineHeight: 1.7,
          }}
        >
          AI-powered cost and timeline estimation for software teams.
          Upload a project document and get a detailed prediction in seconds.
        </p>

        {/* BUTTONS */}
        <div
          style={{
            display: 'flex',
            gap: 12,
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          <Link
            to={session ? '/estimate/new' : '/auth'}
            style={{
              padding: '14px 28px',
              fontSize: '1rem',
              textDecoration: 'none',
              background: 'var(--bg-surface)',
              color: 'var(--text-primary)',
              border: '2px solid var(--text-primary)',
              borderRadius: 10,
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              transition: 'all 0.2s ease',
              cursor: 'pointer',
            }}
          >
            Get Started Free
            <ArrowRight size={18} />
          </Link>

          <a
            href="#how-it-works"
            style={{
              padding: '14px 28px',
              fontSize: '1rem',
              textDecoration: 'none',
              background: 'var(--bg-surface)',
              color: 'var(--text-primary)',
              border: '2px solid var(--text-primary)',
              borderRadius: 10,
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              transition: 'all 0.2s ease',
              cursor: 'pointer',
            }}
          >
            See How It Works
          </a>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section
        id="how-it-works"
        style={{
          padding: '4rem 1.5rem',
          maxWidth: 900,
          margin: '0 auto',
        }}
      >
        <h2
          style={{
            fontSize: '2rem',
            fontWeight: 700,
            textAlign: 'center',
            color: 'var(--text-primary)',
            marginBottom: 48,
          }}
        >
          How It Works
        </h2>

        {steps.map(({ num, title, desc }, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              gap: 20,
              alignItems: 'flex-start',
              padding: '24px 0',
              borderBottom:
                i < steps.length - 1
                  ? '1px solid var(--border-color)'
                  : 'none',
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
              }}
            >
              {num}
            </div>

            <div>
              <h3
                style={{
                  fontWeight: 600,
                  fontSize: '1.0625rem',
                  color: 'var(--text-primary)',
                  marginBottom: 4,
                }}
              >
                {title}
              </h3>
              <p
                style={{
                  fontSize: '0.875rem',
                  color: 'var(--text-secondary)',
                }}
              >
                {desc}
              </p>
            </div>
          </div>
        ))}
      </section>

      {/* CTA */}
      <section
        style={{
          padding: '5rem 1.5rem',
          textAlign: 'center',
        }}
      >
        <h2
          style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            marginBottom: 16,
          }}
        >
          Ready to predict your next project?
        </h2>

        <Link
          to={session ? '/estimate/new' : '/auth'}
          style={{
            padding: '16px 32px',
            fontSize: '1.0625rem',
            background: 'var(--bg-surface)',
            color: 'var(--text-primary)',
            border: '2px solid var(--text-primary)',
            borderRadius: 10,
            textDecoration: 'none',
            fontWeight: 600,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          Start Estimating Now
          <ChevronRight size={18} />
        </Link>
      </section>

      {/* FOOTER */}
      <footer
        style={{
          borderTop: '1px solid var(--border-color)',
          padding: '2rem 1.5rem',
          textAlign: 'center',
          color: 'var(--text-tertiary)',
          fontSize: '0.8125rem',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: 24,
            marginBottom: 12,
            color: 'var(--text-primary)', // auto black/light, white/dark
            flexWrap: 'wrap',
            textAlign: 'center',
          }}
        >
          <span style={{ cursor: 'pointer' }}>Privacy Policy</span>
          <span style={{ cursor: 'pointer' }}>Terms</span>
          <span style={{ cursor: 'pointer' }}>API Docs</span>
          <span style={{ cursor: 'pointer' }}>Contact</span>
        </div>

        <p
          style={{
            color: 'var(--text-primary)', // theme-based
            textAlign: 'center',
            margin: 0,
          }}
        >
          © 2026 PredictIQ. Know Before You Build.
        </p>
      </footer>
    </div>
  );
}
