import React from 'react';

interface LoadingSkeletonProps {
  lines?: number;
  width?: 'full' | '75%' | '50%' | '25%';
  height?: number;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  lines = 3,
  width = 'full',
  height = 20,
}) => {
  const widthMap = {
    full: '100%',
    '75%': '75%',
    '50%': '50%',
    '25%': '25%',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton-pulse"
          style={{
            height: `${height}px`,
            width: i === lines - 1 && lines > 1 ? '60%' : widthMap[width],
            borderRadius: '8px',
            background: 'linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.04) 75%)',
            backgroundSize: '200% 100%',
            animation: 'shimmer 1.5s ease-in-out infinite',
          }}
        />
      ))}
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </div>
  );
};

export default LoadingSkeleton;
