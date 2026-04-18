import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { LogOut, User, LogIn } from 'lucide-react';
import React, { useState, useRef, useEffect } from 'react';
import logoImg from '@/assets/logo.png';

export default function Navbar() {
  const { user, profile, signOut } = useAuthStore();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
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
    setShowMenu(false);
    await signOut();
    navigate('/auth');
  };

  const handleSignIn = () => {
    setShowMenu(false);
    navigate('/auth');
  };

  const menuItemStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '8px 12px',
    borderRadius: 8,
    width: '100%',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
    fontSize: '0.875rem',
    color: 'var(--text-primary)',
    textAlign: 'left' as const,
    transition: 'background 0.15s',
  };

  return (
    <nav
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-color)',
        padding: '0 1.5rem',
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Logo */}
      <Link
        to={user ? '/dashboard' : '/'}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          textDecoration: 'none',
        }}
      >
        <img
          src={logoImg}
          alt="PredictIQ Logo"
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            objectFit: 'contain',
          }}
        />

        <span
          style={{
            fontSize: '1.125rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
          }}
        >
          PredictIQ
          <span
            style={{
              display: 'block',
              fontSize: '0.75rem',
              color: 'var(--text-secondary)',
              margin: 0,
              fontWeight: 400,
            }}
          >
            Designed for Engineers by Engineers
          </span>
        </span>
      </Link>

      {/* User Icon */}
      <div ref={menuRef} style={{ position: 'relative' }}>
        <button
          onClick={() => setShowMenu(!showMenu)}
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #1A56DB, #3B82F6)',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '0.8125rem',
            fontWeight: 600,
          }}
        >
          {user
            ? (profile?.full_name || user.email || '?')[0].toUpperCase()
            : <User size={18} />}
        </button>

        {/* Dropdown Menu */}
        {showMenu && (
          <div
            style={{
              position: 'absolute',
              right: 0,
              top: 44,
              background: 'var(--bg-surface)',
              border: '1px solid #e5e7eb',
              borderRadius: 12,
              padding: 8,
              minWidth: 180,
              boxShadow: '0 10px 20px rgba(0,0,0,0.1)',
            }}
          >
            {/* Show Settings & Sign Out ONLY if logged in */}
            {user && (
              <>
                <button
                  onClick={() => {
                    setShowMenu(false);
                    navigate('/settings');
                  }}
                  style={menuItemStyle}
                >
                  <User size={15} />
                  Settings
                </button>

                <button
                  onClick={handleSignOut}
                  style={{
                    ...menuItemStyle,
                    color: '#EF4444',
                  }}
                >
                  <LogOut size={15} />
                  Sign Out
                </button>
              </>
            )}

            {/* Show Sign In ONLY if logged out */}
            {!user && (
              <button
                onClick={handleSignIn}
                style={menuItemStyle}
              >
                <LogIn size={15} />
                Sign In
              </button>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}