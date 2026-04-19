import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/App';
import { Mail, Lock, User, Eye, EyeOff, GitBranch, ArrowLeft } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import logoImg from '@/assets/logo.png';

type AuthMode = 'landing' | 'login' | 'register' | 'forgot';

export default function AuthPage() {
  const { session, signIn, signUp, signInWithOAuth, loading } = useAuthStore();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [mode, setMode] = useState<AuthMode>('landing');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  if (session) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (mode === 'register') {
      if (password.length < 10) {
        addToast('error', 'Password must be at least 10 characters');
        return;
      }
      if (password !== confirmPassword) {
        addToast('error', 'Passwords do not match');
        return;
      }
    }

    try {
      if (mode === 'login') {
        await signIn(email, password);
        addToast('success', 'Welcome back!');
        navigate('/dashboard');
      } else if (mode === 'register') {
        await signUp(email, password, fullName);
        addToast('success', 'Account created! Check your email for verification.');
        navigate('/dashboard');
      } else if (mode === 'forgot') {
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: window.location.origin + '/auth',
        });
        if (error) throw error;
        addToast('success', 'Password reset link sent! Check your email.');
        setMode('login');
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Authentication failed';
      addToast('error', message);
    }
  };

  const handleOAuth = async (provider: 'google' | 'github') => {
    try {
      await signInWithOAuth(provider);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : `${provider} auth failed`;
      addToast('error', message);
    }
  };

  const showForm = mode !== 'landing';

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      flexDirection: 'column',
      background: 'white',
      position: 'relative', overflow: 'hidden',
    }}>

      {/* ── Top Navbar ───────────────────────────────────── */}
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '16px 32px',
        position: 'relative', zIndex: 2,
        borderBottom: '2px solid black',
      }}>
        {/* Left: Logo + Name */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}
          onClick={() => setMode('landing')}
        >
          <img src={logoImg} alt="PredictIQ" style={{ width: 36, height: 36, objectFit: 'contain' }} />
          <span style={{ fontSize: '1.15rem', fontWeight: 700, color: 'black' }}>
            PredictIQ

          </span>
        </div>

        {/* Right: Sign Up / Login buttons */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button
            onClick={() => setMode('login')}
            style={{
              padding: '8px 20px', borderRadius: 10,
              border: '1.5px solid var(--border-color)',
              background: 'white',
              color: 'black',
              fontWeight: 600, fontSize: '0.85rem',
              cursor: 'pointer', transition: 'all 0.2s',
            }}
          >
            Login
          </button>
          <button
            onClick={() => setMode('register')}
            style={{
              padding: '8px 20px', borderRadius: 10,
              border: '1.5px solid var(--border-color)',
              background: 'white',
              color: 'black',
              fontWeight: 600, fontSize: '0.85rem',
              cursor: 'pointer', transition: 'all 0.2s',
            }}
          >
            Sign Up
          </button>
        </div>
      </nav>

      {/* ── Main Content ─────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', zIndex: 1 }}>

        {/* ── Landing View (branding in center) ──────────── */}
        {!showForm && (
          <div className="animate-fade-in" style={{ textAlign: 'center', maxWidth: 600, padding: '0 24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <img src={logoImg} alt="PredictIQ" style={{ width: 100, height: 100, objectFit: 'contain', marginBottom: 16 }} />
            <h1 style={{
              fontSize: '2.75rem', fontWeight: 800, color: 'black',
              letterSpacing: '-0.03em', lineHeight: 1.15, marginBottom: 16,
            }}>
              PredictIQ
            </h1>
            <p style={{
              fontSize: '1.15rem', color: 'black',
              lineHeight: 1.7, marginBottom: 12,
            }}>
              AI-powered cost estimation for software teams.
              <br />Designed for Engineers by Engineers.
              <br />Upload a doc, get a prediction.
            </p>

            {/* Stats */}
            <div style={{
              display: 'flex', gap: 40, justifyContent: 'center', marginTop: 36,
            }}>
              {[
                { label: 'Accuracy', value: '92%' },
                { label: 'Estimates', value: '10K+' },
                { label: 'Currencies', value: '200+' },
              ].map(({ label, value }) => (
                <div key={label} style={{ textAlign: 'center' }}>
                  <p className="tabular-nums" style={{
                    fontSize: '1.75rem', fontWeight: 700, color: 'black', margin: 0,
                  }}>{value}</p>
                  <p style={{ fontSize: '0.8rem', color: 'black', opacity: 0.7, margin: '4px 0 0' }}>{label}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Auth Form Card ──────────────────────────────── */}
        {showForm && (
          <div className="animate-fade-in" style={{
            width: '100%', maxWidth: 440,
            background: 'var(--bg-surface)', borderRadius: 20,
            border: '1px solid var(--border-color)',
            boxShadow: '0 20px 60px rgba(0,0,0,0.12)',
            padding: 40, margin: '24px',
          }}>
            {/* Header with back button */}
            <div style={{ textAlign: 'center', marginBottom: 28 }}>
              <button
                onClick={() => setMode('landing')}
                style={{
                  position: 'absolute', left: 16, top: 16,
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 4,
                  fontSize: '0.8rem',
                }}
              >
                <ArrowLeft size={14} /> Back
              </button>
              <img src={logoImg} alt="PredictIQ Logo" style={{ width: 48, height: 48, objectFit: 'contain', marginBottom: 12 }} />
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {mode === 'login' ? 'Welcome back' : mode === 'register' ? 'Create account' : 'Reset password'}
              </h1>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                {mode === 'login' ? 'Sign in to your PredictIQ account' :
                  mode === 'register' ? 'Start estimating in seconds' :
                    'Enter your email to reset password'}
              </p>
            </div>

            {/* OAuth buttons */}
            {mode !== 'forgot' && (
              <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
                <button onClick={() => handleOAuth('google')} className="btn-secondary" style={{
                  flex: 1, justifyContent: 'center', padding: '10px 0',
                }}>
                  <svg width="16" height="16" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  Google
                </button>
                <button onClick={() => handleOAuth('github')} className="btn-secondary" style={{
                  flex: 1, justifyContent: 'center', padding: '10px 0',
                }}>
                  <GitBranch size={16} /> GitHub
                </button>
              </div>
            )}

            {mode !== 'forgot' && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: 12, margin: '16px 0',
                color: 'var(--text-tertiary)', fontSize: '0.75rem',
              }}>
                <div style={{ flex: 1, height: 1, background: 'var(--border-color)' }} />
                <span>or continue with email</span>
                <div style={{ flex: 1, height: 1, background: 'var(--border-color)' }} />
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {mode === 'register' && (
                <div>
                  <label className="label">Full Name</label>
                  <div style={{ position: 'relative' }}>
                    <User size={16} style={{
                      position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
                      color: 'var(--text-tertiary)',
                    }} />
                    <input
                      type="text"
                      className="input-field"
                      style={{ paddingLeft: 36 }}
                      placeholder="John Smith"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="label">Email</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} style={{
                    position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--text-tertiary)',
                  }} />
                  <input
                    type="email"
                    className="input-field"
                    style={{ paddingLeft: 36 }}
                    placeholder="you@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>

              {mode !== 'forgot' && (
                <div>
                  <label className="label">Password</label>
                  <div style={{ position: 'relative' }}>
                    <Lock size={16} style={{
                      position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
                      color: 'var(--text-tertiary)',
                    }} />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      className="input-field"
                      style={{ paddingLeft: 36, paddingRight: 40 }}
                      placeholder={mode === 'register' ? 'Min 10 characters' : 'Enter password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      minLength={mode === 'register' ? 10 : undefined}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      style={{
                        position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: 'var(--text-tertiary)', padding: 0,
                      }}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
              )}

              {mode === 'register' && (
                <div>
                  <label className="label">Confirm Password</label>
                  <div style={{ position: 'relative' }}>
                    <Lock size={16} style={{
                      position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
                      color: 'var(--text-tertiary)',
                    }} />
                    <input
                      type="password"
                      className="input-field"
                      style={{ paddingLeft: 36 }}
                      placeholder="Re-enter password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>
              )}

              <button type="submit" className="btn-primary" style={{
                width: '100%', justifyContent: 'center', marginTop: 8, padding: '12px 0',
                opacity: loading ? 0.7 : 1, pointerEvents: loading ? 'none' : 'auto',
              }}>
                {loading ? (
                  <div style={{
                    width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.8s linear infinite',
                  }} />
                ) : (
                  mode === 'login' ? 'Sign In' : mode === 'register' ? 'Create Account' : 'Send Reset Link'
                )}
              </button>
            </form>

            {/* Mode switch */}
            <div style={{
              marginTop: 20, textAlign: 'center', fontSize: '0.8125rem',
              color: 'var(--text-secondary)',
            }}>
              {mode === 'login' ? (
                <>
                  Don&apos;t have an account?{' '}
                  <button onClick={() => setMode('register')} style={{
                    background: 'none', border: 'none', color: 'var(--color-primary)',
                    cursor: 'pointer', fontWeight: 600,
                  }}>Sign up</button>
                  <br />
                  <button onClick={() => setMode('forgot')} style={{
                    background: 'none', border: 'none', color: 'var(--text-tertiary)',
                    cursor: 'pointer', marginTop: 8, fontSize: '0.8125rem',
                  }}>Forgot password?</button>
                </>
              ) : mode === 'register' ? (
                <>
                  Already have an account?{' '}
                  <button onClick={() => setMode('login')} style={{
                    background: 'none', border: 'none', color: 'var(--color-primary)',
                    cursor: 'pointer', fontWeight: 600,
                  }}>Sign in</button>
                </>
              ) : (
                <>
                  Remember your password?{' '}
                  <button onClick={() => setMode('login')} style={{
                    background: 'none', border: 'none', color: 'var(--color-primary)',
                    cursor: 'pointer', fontWeight: 600,
                  }}>Sign in</button>
                </>
              )}
            </div>
          </div>
        )}
      </div>



      {/* Copyright bar */}
      <div style={{
        borderTop: '1px solid #e0e0e0',
        margin: '0 48px',
        padding: '24px 0 20px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexWrap: 'wrap', gap: 16,
        position: 'relative', zIndex: 2,
      }}>
        <p style={{ fontSize: '0.8rem', color: '#888', margin: 0 }}>
          Copyright © {new Date().getFullYear()} PredictIQ
        </p>
        <div style={{ display: 'flex', gap: 24 }}>
          {['Transparency Act', 'Support Policy', 'Security Policy', 'Privacy Policy'].map(link => (
            <span key={link} style={{ fontSize: '0.8rem', color: '#555', cursor: 'pointer' }}>{link}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
