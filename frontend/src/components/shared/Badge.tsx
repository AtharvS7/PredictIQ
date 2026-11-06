import React from 'react';
import { ShieldCheck, Database, Cpu, AlertCircle, CheckCircle2 } from 'lucide-react';

export type BadgeVariant =
  | 'default'
  | 'primary'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'neutral';

export type BadgeSize = 'xs' | 'sm' | 'md';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: BadgeSize;
  pill?: boolean;
  outline?: boolean;
  dot?: boolean;
  dotColor?: string;
  icon?: React.ReactNode;
  className?: string;
}

const variantStyles: Record<BadgeVariant, { filled: string; outline: string; dot: string }> = {
  default: {
    filled: 'bg-[var(--bg-elevated)] text-[var(--text-secondary)] border border-[var(--border-color)]',
    outline: 'border border-[var(--border-color)] text-[var(--text-secondary)] bg-transparent',
    dot: 'bg-[var(--text-tertiary)]',
  },
  primary: {
    filled: 'bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800',
    outline: 'border border-blue-500 text-blue-600 dark:text-blue-400 bg-transparent',
    dot: 'bg-blue-500',
  },
  success: {
    filled: 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800',
    outline: 'border border-emerald-500 text-emerald-600 dark:text-emerald-400 bg-transparent',
    dot: 'bg-emerald-500',
  },
  warning: {
    filled: 'bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800',
    outline: 'border border-amber-500 text-amber-600 dark:text-amber-400 bg-transparent',
    dot: 'bg-amber-500',
  },
  danger: {
    filled: 'bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800',
    outline: 'border border-rose-500 text-rose-600 dark:text-rose-400 bg-transparent',
    dot: 'bg-rose-500',
  },
  info: {
    filled: 'bg-sky-50 text-sky-700 border border-sky-200 dark:bg-sky-950/60 dark:text-sky-300 dark:border-sky-800',
    outline: 'border border-sky-500 text-sky-600 dark:text-sky-400 bg-transparent',
    dot: 'bg-sky-500',
  },
  neutral: {
    filled: 'bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700',
    outline: 'border border-slate-400 text-slate-600 dark:text-slate-300 bg-transparent',
    dot: 'bg-slate-400',
  },
};

const sizeStyles: Record<BadgeSize, string> = {
  xs: 'text-[10px] font-semibold px-1.5 py-0.5 gap-1',
  sm: 'text-xs font-medium px-2 py-0.5 gap-1.5',
  md: 'text-xs font-semibold px-2.5 py-1 gap-1.5',
};

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      variant = 'default',
      size = 'sm',
      pill = true,
      outline = false,
      dot = false,
      dotColor,
      icon,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    const vConfig = variantStyles[variant];
    const shapeClass = pill ? 'rounded-full' : 'rounded-md';
    const variantClass = outline ? vConfig.outline : vConfig.filled;

    return (
      <span
        ref={ref}
        className={`inline-flex items-center tracking-tight transition-colors ${sizeStyles[size]} ${shapeClass} ${variantClass} ${className}`.trim()}
        {...props}
      >
        {dot && (
          <span
            className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColor || vConfig.dot}`}
            aria-hidden="true"
          />
        )}
        {icon && <span className="shrink-0">{icon}</span>}
        <span>{children}</span>
      </span>
    );
  }
);
Badge.displayName = 'Badge';

/* ── Specialized Badge Primitives ────────────────────────────── */

export type DataQualityTier = 'A' | 'B' | 'C';

export interface DataQualityBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tier: DataQualityTier;
  compact?: boolean;
  showIcon?: boolean;
  className?: string;
}

const tierConfig: Record<
  DataQualityTier,
  {
    name: string;
    subtext: string;
    variant: BadgeVariant;
    icon: typeof ShieldCheck;
    glowClass: string;
  }
> = {
  A: {
    name: 'Tier A',
    subtext: 'Certified Benchmark',
    variant: 'success',
    icon: ShieldCheck,
    glowClass: 'shadow-[0_0_12px_rgba(16,185,129,0.25)]',
  },
  B: {
    name: 'Tier B',
    subtext: 'Validated Standard',
    variant: 'info',
    icon: Database,
    glowClass: 'shadow-[0_0_12px_rgba(59,130,246,0.2)]',
  },
  C: {
    name: 'Tier C',
    subtext: 'Heuristic',
    variant: 'warning',
    icon: AlertCircle,
    glowClass: 'shadow-[0_0_12px_rgba(245,158,11,0.2)]',
  },
};

export const DataQualityBadge: React.FC<DataQualityBadgeProps> = ({
  tier,
  compact = false,
  showIcon = true,
  className = '',
  ...props
}) => {
  const config = tierConfig[tier] || tierConfig.B;
  const Icon = config.icon;

  return (
    <Badge
      variant={config.variant}
      size="sm"
      pill
      className={`${config.glowClass} font-semibold ${className}`}
      icon={showIcon ? <Icon size={12} className="stroke-[2.5]" /> : undefined}
      title={`${config.name}: ${config.subtext}`}
      data-tier={tier}
      {...props}
    >
      <span>{config.name}</span>
      {!compact && <span className="opacity-80 font-normal"> • {config.subtext}</span>}
    </Badge>
  );
};

export interface ModelVersionBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  version: string;
  sha256?: string;
  sourcesCount?: number;
  className?: string;
}

export const ModelVersionBadge: React.FC<ModelVersionBadgeProps> = ({
  version,
  sha256,
  sourcesCount,
  className = '',
  ...props
}) => {
  const shortSha = sha256 ? sha256.slice(0, 7) : null;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono bg-[var(--bg-elevated)] border border-[var(--border-color)] text-[var(--text-secondary)] ${className}`.trim()}
      title={sha256 ? `Model Version: ${version} (SHA: ${sha256})` : `Model Version: ${version}`}
      {...props}
    >
      <Cpu size={12} className="text-[var(--color-primary)] shrink-0" />
      <span className="font-semibold text-[var(--text-primary)]">{version}</span>
      {shortSha && (
        <span className="text-[var(--text-tertiary)] opacity-85">#{shortSha}</span>
      )}
      {sourcesCount !== undefined && (
        <span className="px-1.5 py-0.2 rounded text-[10px] bg-[var(--bg-surface)] text-[var(--text-tertiary)] border border-[var(--border-subtle)] font-sans">
          {sourcesCount} sources
        </span>
      )}
    </span>
  );
};

export interface UncertaintyBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  interval?: string; // e.g. "80% CI [p10–p90]"
  coverage?: string; // e.g. "90% Conformal"
  calibrated?: boolean;
  className?: string;
}

export const UncertaintyBadge: React.FC<UncertaintyBadgeProps> = ({
  interval = '80% CI (p10–p90)',
  coverage,
  calibrated = true,
  className = '',
  ...props
}) => {
  return (
    <Badge
      variant={calibrated ? 'primary' : 'warning'}
      size="sm"
      pill
      dot
      dotColor={calibrated ? 'bg-blue-500' : 'bg-amber-500'}
      className={className}
      icon={calibrated ? <CheckCircle2 size={11} /> : <AlertCircle size={11} />}
      title={calibrated ? 'Statistically calibrated confidence interval' : 'Uncalibrated heuristic estimate'}
      {...props}
    >
      <span>{interval}</span>
      {coverage && <span className="opacity-80"> • {coverage}</span>}
    </Badge>
  );
};

export default Badge;
