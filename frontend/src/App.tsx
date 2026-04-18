import { useEffect, useState, createContext, useContext, type ReactNode } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useCurrencyStore } from '@/store/currencyStore';
import ErrorBoundary from '@/components/ErrorBoundary';
import LandingPage from '@/pages/LandingPage';
import AuthPage from '@/pages/AuthPage';
import DashboardPage from '@/pages/DashboardPage';
import NewEstimatePage from '@/pages/NewEstimatePage';
import ResultsPage from '@/pages/ResultsPage';
import EstimatesPage from '@/pages/EstimatesPage';
import SettingsPage from '@/pages/SettingsPage';
import './index.css';

// ── Theme Context ────────────────────────────────────────
interface ThemeContextType {
  theme: string;
  setTheme: (theme: string) => void;
}

export const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark',
  setTheme: () => { },
});

export const useTheme = () => useContext(ThemeContext);

function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState(() => {
    const saved = localStorage.getItem('predictiq-theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  const setTheme = (newTheme: string) => {
    if (newTheme === 'system') {
      const sys = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', sys);
    } else {
      document.documentElement.setAttribute('data-theme', newTheme);
    }
    localStorage.setItem('predictiq-theme', newTheme);
    setThemeState(newTheme);
  };

  useEffect(() => {
    setTheme(theme);
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// ── Toast Management ─────────────────────────────────────
interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (type: Toast['type'], message: string) => void;
  removeToast: (id: string) => void;
}

export const ToastContext = createContext<ToastContextType>({
  toasts: [],
  addToast: () => { },
  removeToast: () => { },
});

export const useToast = () => useContext(ToastContext);

function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (type: Toast['type'], message: string) => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => removeToast(id), 5000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`toast toast-${toast.type}`}
            onClick={() => removeToast(toast.id)}
          >
            {toast.type === 'success' && '✓'}
            {toast.type === 'error' && '✕'}
            {toast.type === 'info' && 'ℹ'}
            <span>{toast.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

// ── Auth Guard ───────────────────────────────────────────
function RequireAuth({ children }: { children: ReactNode }) {
  const { session, initialized } = useAuthStore();

  if (!initialized) {
    return (
      <div style={{
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        height: '100vh', background: 'var(--bg-primary)',
      }}>
        <div style={{
          width: 40, height: 40, border: '3px solid var(--border-color)',
          borderTopColor: 'var(--color-primary)', borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/auth" replace />;
  }

  return <>{children}</>;
}

// ── App ──────────────────────────────────────────────────
export default function App() {
  const { initialize, initialized } = useAuthStore();

  useEffect(() => {
    initialize();
    // Pre-fetch exchange rates on app mount
    useCurrencyStore.getState().fetchRates();
  }, [initialize]);

  if (!initialized) {
    return (
      <div style={{
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        height: '100vh', background: '#0F172A', color: '#F1F5F9',
        flexDirection: 'column', gap: 16,
      }}>
        <div style={{
          width: 48, height: 48, border: '3px solid #334155',
          borderTopColor: '#1A56DB', borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
        <p style={{ fontFamily: 'Inter, sans-serif', fontWeight: 500 }}>Loading PredictIQ...</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route
                path="/dashboard"
                element={<RequireAuth><DashboardPage /></RequireAuth>}
              />
              <Route
                path="/estimate/new"
                element={<RequireAuth><NewEstimatePage /></RequireAuth>}
              />
              <Route
                path="/estimate/:id/results"
                element={<RequireAuth><ResultsPage /></RequireAuth>}
              />
              <Route
                path="/estimates"
                element={<RequireAuth><EstimatesPage /></RequireAuth>}
              />
              <Route
                path="/settings"
                element={<RequireAuth><SettingsPage /></RequireAuth>}
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
