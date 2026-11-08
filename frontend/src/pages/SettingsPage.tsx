import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import SEOHead from '@/components/shared/SEOHead';
import { useAuthStore } from '@/store/authStore';
import { useCurrencyStore } from '@/store/currencyStore';
import { useTheme, useToast } from '@/App';
import { User, DollarSign, Save, LogOut, Shield } from 'lucide-react';

export default function SettingsPage() {
  const { profile, updateProfile, signOut } = useAuthStore();
  const { theme } = useTheme();
  const { addToast } = useToast();
  const navigate = useNavigate();

  // Untouched fields follow asynchronously loaded profile data; edits take priority.
  const [nameEdit, setFullName] = useState<string | null>(null);
  const [rateEdit, setHourlyRate] = useState<string | null>(null);
  const [currencyEdit, setCurrency] = useState<string | null>(null);
  const fullName = nameEdit ?? profile?.full_name ?? '';
  const hourlyRate = rateEdit ?? profile?.hourly_rate_usd?.toString() ?? '75';
  const currency = currencyEdit ?? profile?.currency ?? 'USD';
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const cardStyle = {
    padding: 24,
    marginBottom: 20,
    border: '1px solid var(--border-color)',
    borderRadius: 12,
    background: 'var(--bg-surface)',
  };

  const handleSave = async () => {
    const rate = Number(hourlyRate);
    if (!hourlyRate.trim() || !Number.isFinite(rate) || rate < 10 || rate > 500) {
      setSaveError('Enter an hourly rate between 10 and 500 USD.');
      return;
    }
    setSaveError(null);
    setSaving(true);

    try {
      await updateProfile({
        full_name: fullName,
        hourly_rate_usd: rate,
        currency,
        theme,
      });
      useCurrencyStore.getState().setCurrency(currency);

      addToast('success', 'Settings saved!');
    } catch {
      setSaveError('Could not save settings. Your changes are preserved; please try again.');
      addToast('error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await signOut();
    navigate('/');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg-primary)',
      }}
    >
      <SEOHead title="Settings" description="PredictIQ v2.0 Monotone Power-Law with Mondrian Split-Conformal Prediction & Empirical Bayes Shrinkage." />
      <Navbar />

      <div style={{ display: 'flex' }}>
        <Sidebar />

        <main
          style={{
            flex: 1,
            padding: 'clamp(1rem, 3vw, 2rem)',
            maxWidth: 700,
            margin: '0 auto',
            minWidth: 0,
          }}
        >
          <h1
            style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              marginBottom: 24,
              color: 'var(--text-primary)',
            }}
          >
            Settings
          </h1>

          <form noValidate onSubmit={(event) => { event.preventDefault(); void handleSave(); }}>
          {saveError && <p role="alert" style={{ color: 'var(--color-danger)', marginBottom: 16 }}>{saveError}</p>}
          {/* Profile */}

          <div className="card" style={cardStyle}>
            <h3
              style={{
                fontWeight: 600,
                marginBottom: 16,
                display: 'flex',
                gap: 8,
                alignItems: 'center',
                color: 'var(--text-primary)',
              }}
            >
              <User size={18} /> Profile
            </h3>

            <label className="label" htmlFor="settings-name">Full Name</label>

            <input
              id="settings-name"
              autoComplete="name"
              maxLength={200}
              className="input-field"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Smith"
            />
          </div>

          {/* Default Rate */}

          <div className="card" style={cardStyle}>
            <h3
              style={{
                fontWeight: 600,
                marginBottom: 16,
                display: 'flex',
                gap: 8,
                alignItems: 'center',
                color: 'var(--text-primary)',
              }}
            >
              <DollarSign size={18} /> Default Rate
            </h3>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 180px), 1fr))',
                gap: 14,
              }}
            >
              <div>
                <label className="label" htmlFor="settings-rate">Hourly Rate (USD)</label>

                <input
                  id="settings-rate"
                  aria-describedby="settings-rate-help"
                  type="number"
                  className="input-field"
                  value={hourlyRate}
                  onChange={(e) => setHourlyRate(e.target.value)}
                  min={10}
                  max={500}
                  step="any"
                />
                <p id="settings-rate-help" style={{ color: 'var(--text-secondary)', fontSize: 12 }}>10–500 USD per hour. Display currency does not change this amount.</p>
              </div>

              <div>
                <label className="label" htmlFor="settings-currency">Display Currency</label>

                <select
                  id="settings-currency"
                  className="input-field"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="INR">INR</option>
                  {!['USD', 'EUR', 'GBP', 'INR'].includes(currency) && <option value={currency}>{currency}</option>}
                </select>
              </div>
            </div>
          </div>

          {/* Empirical-Bayes Calibration & Project Actuals */}
          <div className="card" style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
              <h3
                style={{
                  fontWeight: 600,
                  display: 'flex',
                  gap: 8,
                  alignItems: 'center',
                  color: 'var(--text-primary)',
                  margin: 0,
                }}
              >
                <Shield size={18} className="text-blue-600 dark:text-blue-400" /> Empirical-Bayes Calibration &amp; Actuals
              </h3>
              <span
                style={{
                  fontSize: '0.75rem',
                  padding: '3px 8px',
                  borderRadius: 6,
                  fontWeight: 600,
                  backgroundColor: 'rgba(16, 185, 129, 0.12)',
                  color: 'var(--color-success)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                }}
              >
                Active (R05 Pipeline)
              </span>
            </div>

            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 14 }}>
              PredictIQ v2.0 Monotone Power-Law with Mondrian Split-Conformal Prediction &amp; Empirical Bayes Shrinkage. Delivered projects logged with explicit consent calibrate your organization&apos;s productivity velocity via conjugate normal shrinkage (w<sub>k</sub> = k / (k + 2.83)).
            </p>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 180px), 1fr))',
                gap: 12,
                padding: '12px 14px',
                borderRadius: 8,
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-subtle, var(--border-color))',
                marginBottom: 16,
              }}
            >
              <div>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.04em', display: 'block' }}>
                  Shrinkage Ratio
                </span>
                <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                  &sigma;&sup2; / &tau;&sup2; = 2.83
                </span>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-secondary)', display: 'block' }}>
                  Between-org prior variance
                </span>
              </div>

              <div>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.04em', display: 'block' }}>
                  Empirical Gain
                </span>
                <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--color-success)', fontFamily: 'monospace' }}>
                  +19.52% MdAPE
                </span>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-secondary)', display: 'block' }}>
                  Verified at k=10 actuals
                </span>
              </div>

              <div>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.04em', display: 'block' }}>
                  Safety Guardrail
                </span>
                <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                  [0.33, 3.0]
                </span>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-secondary)', display: 'block' }}>
                  Bounded scaling multiplier
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ color: 'var(--color-success)', fontWeight: 'bold' }}>&bull;</span>
                <span>Consent for retraining is collected per completed project delivery.</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ color: 'var(--color-primary)', fontWeight: 'bold' }}>&bull;</span>
                <span>Up to 20 historical actuals are dynamically pooled into future estimate inference.</span>
              </div>
            </div>

            {profile?.role === 'admin' && (
              <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border-color)', display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Admin Consented Actuals Export:
                </span>
                <a
                  href="/api/v1/admin/actuals/export?format=csv"
                  download="consented_actuals.csv"
                  className="btn-secondary"
                  style={{ textDecoration: 'none', padding: '6px 12px', fontSize: '0.75rem' }}
                >
                  Download CSV
                </a>
                <a
                  href="/api/v1/admin/actuals/export?format=json"
                  download="consented_actuals.json"
                  className="btn-secondary"
                  style={{ textDecoration: 'none', padding: '6px 12px', fontSize: '0.75rem' }}
                >
                  Download JSON
                </a>
              </div>
            )}
          </div>

          {/* Save Changes — SAME THEME LOGIC AS ESTIMATE PAGE */}

          <button
            type="submit"
            disabled={saving}
            style={{
              padding: '10px 18px',
              borderRadius: 8,

              background: 'transparent',

              color: 'var(--text-primary)',

              border: '1px solid var(--text-primary)',

              cursor: 'pointer',

              display: 'flex',
              alignItems: 'center',
              gap: 6,

              transition: 'all 0.2s',

              opacity: saving ? 0.7 : 1,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background =
                'var(--text-primary)';
              e.currentTarget.style.color =
                'var(--bg-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background =
                'transparent';
              e.currentTarget.style.color =
                'var(--text-primary)';
            }}
          >
            <Save size={16} />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          </form>

          {/* Logout */}

          <div
            className="card"
            style={{
              ...cardStyle,
              marginTop: 20,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 16,
            }}
          >
            <div>
              <h3
                style={{
                  fontWeight: 600,
                  marginBottom: 4,
                  display: 'flex',
                  gap: 8,
                  alignItems: 'center',
                  color: 'var(--text-primary)',
                }}
              >
                <LogOut size={18} /> Sign Out
              </h3>

              <p
                style={{
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                  margin: 0,
                }}
              >
                Sign out of your Predictify account
              </p>
            </div>

            <button
              onClick={handleLogout}
              style={{
                padding: '10px 24px',
                borderRadius: 12,
                border: '2px solid #ef4444',
                background: 'rgba(239, 68, 68, 0.08)',
                color: '#ef4444',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background =
                  '#ef4444';
                e.currentTarget.style.color = '#fff';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background =
                  'rgba(239, 68, 68, 0.08)';
                e.currentTarget.style.color = '#ef4444';
              }}
            >
              <LogOut size={16} /> Logout
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}
