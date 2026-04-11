import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useTheme } from '@/App';
import { Sun, Moon, LogOut, User, BarChart3 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

export default function Navbar() {
  const { user, profile, signOut } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowMenu(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  const isDark = theme === 'dark' || (theme === 'system' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches);

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 50,
      background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-color)',
      padding: '0 1.5rem', height: 64,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      backdropFilter: 'blur(12px)',
    }}>
      <Link to={user ? '/dashboard' : '/'} style={{
        display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none',
      }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: 'linear-gradient(135deg, #1A56DB, #3B82F6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <BarChart3 size={18} color="white" />
        </div>
        <span style={{
          fontSize: '1.125rem', fontWeight: 700, color: 'var(--text-primary)',
          letterSpacing: '-0.025em',
        }}>
          PredictIQ
        </span>
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <button
          onClick={() => setTheme(isDark ? 'light' : 'dark')}
          style={{
            width: 36, height: 36, borderRadius: 8, border: '1px solid var(--border-color)',
            background: 'transparent', cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)',
            transition: 'all 0.2s',
          }}
          title="Toggle theme"
        >
          {isDark ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        {user && (
          <div ref={menuRef} style={{ position: 'relative' }}>
            <button
              onClick={() => setShowMenu(!showMenu)}
              style={{
                width: 36, height: 36, borderRadius: '50%',
                background: 'linear-gradient(135deg, #1A56DB, #3B82F6)',
                border: 'none', cursor: 'pointer', display: 'flex',
                alignItems: 'center', justifyContent: 'center', color: 'white',
                fontSize: '0.8125rem', fontWeight: 600,
              }}
            >
              {(profile?.full_name || user.email || '?')[0].toUpperCase()}
            </button>

            {showMenu && (
              <div style={{
                position: 'absolute', right: 0, top: 44,
                background: 'var(--bg-surface)', border: '1px solid var(--border-color)',
                borderRadius: 12, boxShadow: 'var(--shadow-lg)',
                padding: 8, minWidth: 200, animation: 'fadeIn 0.15s ease',
              }}>
                <div style={{
                  padding: '8px 12px', borderBottom: '1px solid var(--border-color)',
                  marginBottom: 4,
                }}>
                  <p style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                    {profile?.full_name || 'User'}
                  </p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    {user.email}
                  </p>
                </div>
                <Link
                  to="/settings"
                  onClick={() => setShowMenu(false)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    padding: '8px 12px', borderRadius: 8, textDecoration: 'none',
                    color: 'var(--text-primary)', fontSize: '0.875rem',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-elevated)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <User size={15} /> Settings
                </Link>
                <button
                  onClick={handleSignOut}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    padding: '8px 12px', borderRadius: 8, width: '100%',
                    border: 'none', background: 'transparent', cursor: 'pointer',
                    color: '#EF4444', fontSize: '0.875rem', textAlign: 'left',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-elevated)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <LogOut size={15} /> Sign out
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
