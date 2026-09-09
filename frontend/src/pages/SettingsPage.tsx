import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import SEOHead from '@/components/shared/SEOHead';
import { useAuthStore } from '@/store/authStore';
import { useCurrencyStore } from '@/store/currencyStore';
import { useTheme, useToast } from '@/App';
import { User, DollarSign, Save, LogOut } from 'lucide-react';

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
      <SEOHead title="Settings" description="Manage your Predictify account, profile, and application preferences." />
      <Navbar />

      <div style={{ display: 'flex' }}>
        <Sidebar />

        <main
          style={{
            flex: 1,
            padding: '2rem',
            maxWidth: 700,
            margin: '0 auto',
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
