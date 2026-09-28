import { Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import Navbar from '@/components/shared/Navbar';
import SEOHead from '@/components/shared/SEOHead';
import {
  ArrowRight,
  ChevronRight,
} from 'lucide-react';

const steps = [
  { num: '01', title: 'Define the work', desc: 'Break your project into tasks you can review' },
  { num: '02', title: 'Set your assumptions', desc: 'Enter low, likely and high effort hours and a rate for each task' },
  { num: '03', title: 'Review the scenarios', desc: 'See the calculated cost range, including your chosen contingency' },
  { num: '04', title: 'Keep a planning record', desc: 'Save budgets privately and revisit the assumptions behind them' },
];

export default function LandingPage() {
  const { session } = useAuthStore();

  return (
    <div style={{ minHeight: '100vh' }}>
      <SEOHead
        title="Software Project Budget Planning"
        description="Build transparent project budgets from task hours, rates and contingency. Save your assumptions and compare cost scenarios."
      />
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
          Plan Your Project Budget{' '}
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
          Turn your task hours and rates into a clear, saved project budget.
          Automatic ML predictions are under validation and are not currently available.
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
            to={session ? '/budgets' : '/auth'}
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
          Ready to plan your next project?
        </h2>

        <Link
          to={session ? '/budgets' : '/auth'}
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
          Start Planning Now
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
          © 2026 Predictify. Know Before You Build.
        </p>
      </footer>
    </div>
  );
}
