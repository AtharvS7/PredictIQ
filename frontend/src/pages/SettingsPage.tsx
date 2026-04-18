import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import { useAuthStore } from '@/store/authStore';
import { useTheme, useToast } from '@/App';
import { User, DollarSign, Palette, Save, LogOut } from 'lucide-react';

export default function SettingsPage() {
  const { profile, updateProfile, signOut } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState(profile?.full_name || '');
  const [hourlyRate, setHourlyRate] = useState(profile?.hourly_rate_usd?.toString() || '75');
  const [currency, setCurrency] = useState(profile?.currency || 'USD');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile({
        full_name: fullName,
        hourly_rate_usd: parseFloat(hourlyRate) || 75,
        currency,
        theme,
      });
      addToast('success', 'Settings saved!');
    } catch {
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
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: 700, margin: '0 auto' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 24, color: 'var(--text-primary)' }}>Settings</h1>

          {/* Profile */}
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontWeight: 600, marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center', color: 'var(--text-primary)' }}>
              <User size={18} /> Profile
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label className="label">Full Name</label>
                <input
                  className="input-field"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="John Smith"
                />
              </div>
            </div>
          </div>

          {/* Default Rate */}
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontWeight: 600, marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center', color: 'var(--text-primary)' }}>
              <DollarSign size={18} /> Default Rate
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div>
                <label className="label">Hourly Rate</label>
                <input
                  type="number"
                  className="input-field"
                  value={hourlyRate}
                  onChange={(e) => setHourlyRate(e.target.value)}
                  min={10} max={500}
                />
              </div>
              <div>
                <label className="label">Currency</label>
                <select
                  className="input-field"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="INR">INR</option>
                </select>
              </div>
            </div>
          </div>

          {/* Appearance 
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontWeight: 600, marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center', color: 'var(--text-primary)' }}>
              <Palette size={18} /> Appearance
            </h3>
            <div style={{ display: 'flex', gap: 12 }}>
              {['light', 'dark', 'system'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t)}
                  style={{
                    flex: 1, padding: '12px 16px', borderRadius: 12,
                    border: `2px solid ${theme === t ? 'var(--color-primary)' : 'var(--border-color)'}`,
                    background: theme === t ? '#c1ace80d' : 'var(--bg-surface)',
                    cursor: 'pointer', fontWeight: 500, fontSize: '0.875rem',
                    color: theme === t ? 'var(--color-primary)' : 'var(--text-secondary)',
                    transition: 'all 0.2s', textTransform: 'capitalize',
                  }}
                >
                  {t}
                </button>
              ))}
            </div>
          </div> */}

          {/* Save */}
          <button className="btn-primary" onClick={handleSave} disabled={saving} style={{
            opacity: saving ? 0.7 : 1,
          }}>
            <Save size={16} /> {saving ? 'Saving...' : 'Save Changes'}
          </button>

          {/* Logout */}
          <div className="card" style={{ padding: 24, marginTop: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ fontWeight: 600, marginBottom: 4, display: 'flex', gap: 8, alignItems: 'center', color: 'var(--text-primary)' }}>
                <LogOut size={18} /> Sign Out
              </h3>
              {/*<p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>
                Sign out of your PredictIQ account
              </p>*/}
            </div>
            <button
              id="logout-button"
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
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#ef4444';
                e.currentTarget.style.color = '#fff';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(239, 68, 68, 0.08)';
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
