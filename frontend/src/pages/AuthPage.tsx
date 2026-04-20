import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/App';
import Navbar from '@/components/shared/Navbar';
import logoImg from '@/assets/logo.png';
import { Mail, Lock, User, Eye, EyeOff, GitBranch } from 'lucide-react';

type AuthMode = 'login' | 'register' | 'forgot';

export default function AuthPage() {
  const { session, signIn, signUp, signInWithOAuth, loading } = useAuthStore();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [mode, setMode] = useState<AuthMode>('login');
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

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--bg-primary)'
    }}>

      {/* Navigation Bar */}
      <Navbar />

      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24
      }}>

        <div className="animate-fade-in" style={{
          width: '100%',
          maxWidth: 420,
          background: 'var(--bg-surface)',
          borderRadius: 20,
          border: '2px solid var(--text-primary)',
          padding: 40
        }}>

          {/* Logo Image */}
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <img
              src={logoImg}
              alt="PredictIQ Logo"
              style={{
                width: 56,
                height: 56,
                objectFit: 'contain',
                display: 'block',
                margin: '0 auto 16px'
              }}
            />

            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              color: 'var(--text-primary)'
            }}>
              {mode === 'login'
                ? 'Welcome back'
                : mode === 'register'
                  ? 'Create account'
                  : 'Reset password'}
            </h1>
          </div>

          {/* OAuth buttons */}
          {mode !== 'forgot' && (
            <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
              <button
                onClick={() => handleOAuth('google')}
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  padding: '10px 0',
                  borderRadius: 8,
                  border: '1px solid var(--text-primary)',
                  background: 'transparent',
                  color: 'var(--text-primary)',
                  cursor: 'pointer'
                }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" style={{ display: 'block' }}>
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                <span>Google</span>
              </button>

              <button
                onClick={() => handleOAuth('github')}
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  padding: '10px 0',
                  borderRadius: 8,
                  border: '1px solid var(--text-primary)',
                  background: 'transparent',
                  color: 'var(--text-primary)',
                  cursor: 'pointer'
                }}
              >
                <GitBranch size={18} style={{ display: 'block' }} /> GitHub
              </button>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

            {mode === 'register' && (
              <div>
                <label className="label">Full Name</label>
                <div style={{ position: 'relative' }}>
                  <User size={16} style={{
                    position: 'absolute',
                    left: 12,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-tertiary)'
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
                  position: 'absolute',
                  left: 12,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-tertiary)'
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
                    position: 'absolute',
                    left: 12,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-tertiary)'
                  }} />

                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="input-field"
                    style={{ paddingLeft: 36, paddingRight: 40 }}
                    placeholder={mode === 'register'
                      ? 'Min 10 characters'
                      : 'Enter password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={mode === 'register' ? 10 : undefined}
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: 'absolute',
                      right: 12,
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: 'var(--text-tertiary)'
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
                    position: 'absolute',
                    left: 12,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-tertiary)'
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

            {/* Sign In / Register Button — color removed */}
            <button
              type="submit"
              style={{
                width: '100%',
                padding: '12px 0',
                borderRadius: 8,
                border: '2px solid var(--text-primary)',
                background: 'transparent',
                color: 'var(--text-primary)',
                fontWeight: 600,
                cursor: 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading
                ? 'Processing...'
                : mode === 'login'
                  ? 'Sign In'
                  : mode === 'register'
                    ? 'Create Account'
                    : 'Send Reset Link'}
            </button>

          </form>

          {/* Mode switch */}
          <div style={{
            marginTop: 20,
            textAlign: 'center',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)'
          }}>

            {mode === 'login' ? (
              <>
                Don&apos;t have an account?{' '}
                <button
                  onClick={() => setMode('register')}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'black',
                    cursor: 'pointer',
                    fontWeight: 600
                  }}
                >
                  Sign up
                </button>

                <br />

                <button
                  onClick={() => setMode('forgot')}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'red',
                    cursor: 'pointer',
                    marginTop: 8,
                    fontSize: '0.85rem',
                    fontWeight: 600
                  }}
                >
                  Forgot password?
                </button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button
                  onClick={() => setMode('login')}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'black',
                    cursor: 'pointer',
                    fontWeight: 600
                  }}
                >
                  Sign in
                </button>
              </>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
