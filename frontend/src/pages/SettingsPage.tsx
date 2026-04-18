import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';
import { useAuthStore } from '@/store/authStore';
import { useToast, useTheme } from '@/App';
import { supabase } from '@/lib/supabase';
import { User, DollarSign, Save, LogOut, Phone, Lock } from 'lucide-react';

export default function SettingsPage() {
  const { profile, updateProfile, signOut } = useAuthStore();
  const { theme } = useTheme();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState(profile?.full_name || '');
  const [hourlyRate, setHourlyRate] = useState(
    profile?.hourly_rate_usd?.toString() || '75'
  );
  const [currency, setCurrency] = useState(profile?.currency || 'USD');
  const [phone, setPhone] = useState(profile?.phone || '');
  const [saving, setSaving] = useState(false);

  const countryDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        countryDropdownRef.current &&
        !countryDropdownRef.current.contains(e.target as Node)
      ) {
        // dropdown closed (if implemented later)
      }
    };

    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);

  const handleSave = async () => {
    setSaving(true);

    try {
      await updateProfile({
        full_name: fullName,
        hourly_rate_usd: parseFloat(hourlyRate) || 75,
        currency,
        theme,
        phone,
      });

      addToast('success', 'Settings saved!');
    } catch {
      addToast('error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword.length < 10) {
      addToast('error', 'Password must be at least 10 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      addToast('error', 'Passwords do not match');
      return;
    }

    setChangingPassword(true);

    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });

      if (error) throw error;

      addToast('success', 'Password updated successfully!');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : 'Failed to update password';

      addToast('error', message);
    } finally {
      setChangingPassword(false);
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

          {/* Profile */}
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
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

            <label className="label">Full Name</label>

            <input
              className="input-field"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Smith"
            />
          </div>

          {/* Contact 
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
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
              <Phone size={18} /> Contact Number
            </h3>
*/}
          {/* <label className="label">Phone Number</label>

            <input
              type="tel"
              className="input-field"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="1234567890"
            />
          </div>  */}

          {/* Default Rate */}
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
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
                gridTemplateColumns: '1fr 1fr',
                gap: 14,
              }}
            >
              <div>
                <label className="label">Hourly Rate</label>

                <input
                  type="number"
                  className="input-field"
                  value={hourlyRate}
                  onChange={(e) =>
                    setHourlyRate(e.target.value)
                  }
                  min={10}
                  max={500}
                />
              </div>

              <div>
                <label className="label">Currency</label>

                <select
                  className="input-field"
                  value={currency}
                  onChange={(e) =>
                    setCurrency(e.target.value)
                  }
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="INR">INR</option>
                </select>
              </div>
            </div>
          </div>

          {/* Change Password */}
          <div className="card" style={{ padding: 24, marginBottom: 20 }}>
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
              <Lock size={18} /> Change Password
            </h3>

            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 14,
              }}
            >
              <input
                type="password"
                className="input-field"
                value={newPassword}
                onChange={(e) =>
                  setNewPassword(e.target.value)
                }
                placeholder="Min 10 characters"
              />

              <input
                type="password"
                className="input-field"
                value={confirmPassword}
                onChange={(e) =>
                  setConfirmPassword(e.target.value)
                }
                placeholder="Re-enter new password"
              />

              <button
                onClick={handleChangePassword}
                disabled={
                  changingPassword ||
                  !newPassword ||
                  !confirmPassword
                }
                className="btn-secondary"
                style={{
                  alignSelf: 'flex-start',
                  padding: '10px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <Lock size={14} />
                {changingPassword
                  ? 'Updating...'
                  : 'Update Password'}
              </button>
            </div>
          </div>

          {/* Save + Logout */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              gap: 16,
              marginTop: 24,
            }}
          >
            <button
              className="btn-primary"
              onClick={handleSave}
              disabled={saving}
              style={{
                flex: 1,
                maxWidth: 220,
                padding: '12px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
              }}
            >
              <Save size={16} />
              {saving ? 'Saving...' : 'Save Changes'}
            </button>

            <button
              onClick={handleLogout}
              style={{
                flex: 1,
                maxWidth: 220,
                padding: '12px 24px',
                borderRadius: 12,
                border: '2px solid #ef4444',
                background: 'rgba(239,68,68,0.08)',
                color: '#ef4444',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
              }}
            >
              <LogOut size={16} />
              Sign Out
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}