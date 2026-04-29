import React, { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });
    console.error('[Predictify ErrorBoundary]', error, errorInfo);
  }

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      const isDev = import.meta.env.DEV;

      return (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: 'var(--bg-primary, #0a0a0f)',
          padding: '2rem',
        }}>
          <div style={{
            background: 'var(--bg-secondary, #12121a)',
            borderRadius: '16px',
            padding: '3rem',
            maxWidth: '520px',
            width: '100%',
            textAlign: 'center',
            border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          }}>
            {/* Error icon */}
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'rgba(239, 68, 68, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
            }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
            </div>

            <h2 style={{
              color: 'var(--text-primary, #fff)',
              fontSize: '1.5rem',
              fontWeight: 700,
              margin: '0 0 0.75rem',
              fontFamily: "'Inter', system-ui, sans-serif",
            }}>
              Something went wrong
            </h2>

            <p style={{
              color: 'var(--text-secondary, #a0a0b0)',
              fontSize: '0.95rem',
              lineHeight: 1.6,
              margin: '0 0 2rem',
              fontFamily: "'Inter', system-ui, sans-serif",
            }}>
              An unexpected error occurred. Please refresh the page to continue using Predictify.
            </p>

            <button
              onClick={this.handleReload}
              style={{
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                color: '#fff',
                border: 'none',
                borderRadius: '10px',
                padding: '12px 32px',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: 'pointer',
                fontFamily: "'Inter', system-ui, sans-serif",
                transition: 'transform 0.15s, box-shadow 0.15s',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(99, 102, 241, 0.4)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              Reload Page
            </button>

            {/* Dev-only error details */}
            {isDev && this.state.error && (
              <details style={{
                marginTop: '2rem',
                textAlign: 'left',
                background: 'rgba(239, 68, 68, 0.05)',
                borderRadius: '8px',
                padding: '1rem',
                border: '1px solid rgba(239, 68, 68, 0.15)',
              }}>
                <summary style={{
                  color: '#EF4444',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  fontFamily: "'Inter', system-ui, sans-serif",
                }}>
                  Error Details (Development Only)
                </summary>
                <pre style={{
                  color: '#f87171',
                  fontSize: '0.8rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                  marginTop: '0.75rem',
                  fontFamily: "'Fira Code', monospace",
                  lineHeight: 1.5,
                }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
