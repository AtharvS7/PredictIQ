import React from 'react';

interface EmptyStateProps {
  icon?: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon = '📊',
  title,
  description,
  actionLabel,
  onAction,
}) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '4rem 2rem',
      textAlign: 'center',
    }}>
      <div style={{
        fontSize: '3rem',
        marginBottom: '1.5rem',
        opacity: 0.6,
      }}>
        {icon}
      </div>

      <h3 style={{
        color: 'var(--text-primary, #fff)',
        fontSize: '1.25rem',
        fontWeight: 600,
        margin: '0 0 0.75rem',
        fontFamily: "'Inter', system-ui, sans-serif",
      }}>
        {title}
      </h3>

      <p style={{
        color: 'var(--text-secondary, #a0a0b0)',
        fontSize: '0.9rem',
        lineHeight: 1.6,
        maxWidth: '400px',
        margin: '0 0 1.5rem',
        fontFamily: "'Inter', system-ui, sans-serif",
      }}>
        {description}
      </p>

      {actionLabel && onAction && (
        <button
          onClick={onAction}
          style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            color: '#fff',
            border: 'none',
            borderRadius: '10px',
            padding: '10px 24px',
            fontSize: '0.9rem',
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
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
