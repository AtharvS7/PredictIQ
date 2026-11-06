import React from 'react';

export type HeadingLevel = 1 | 2 | 3 | 4 | 5 | 6;

export interface HeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  level?: HeadingLevel;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'div' | 'span';
  variant?: 'display' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
  className?: string;
}

const headingVariants: Record<string, string> = {
  display: 'text-3xl sm:text-4xl font-extrabold tracking-tight text-[var(--text-primary)] leading-tight',
  h1: 'text-2xl sm:text-3xl font-bold tracking-tight text-[var(--text-primary)] leading-snug',
  h2: 'text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)] leading-snug',
  h3: 'text-lg sm:text-xl font-semibold tracking-tight text-[var(--text-primary)] leading-normal',
  h4: 'text-base sm:text-lg font-semibold tracking-normal text-[var(--text-primary)] leading-normal',
  h5: 'text-sm sm:text-base font-semibold tracking-normal text-[var(--text-primary)]',
  h6: 'text-xs sm:text-sm font-semibold tracking-wide uppercase text-[var(--text-secondary)]',
};

export const Heading = React.forwardRef<HTMLHeadingElement, HeadingProps>(
  ({ level = 2, as, variant, className = '', children, ...props }, ref) => {
    const Component = (as || `h${level}`) as React.ElementType;
    const vKey = variant || `h${level}`;
    const vClass = headingVariants[vKey] || headingVariants.h2;

    return (
      <Component ref={ref} className={`${vClass} ${className}`.trim()} {...props}>
        {children}
      </Component>
    );
  }
);
Heading.displayName = 'Heading';

export type TextVariant =
  | 'body'
  | 'body-sm'
  | 'body-lg'
  | 'caption'
  | 'overline'
  | 'muted'
  | 'mono';

export interface TextProps extends React.HTMLAttributes<HTMLElement> {
  as?: 'p' | 'span' | 'div' | 'label';
  variant?: TextVariant;
  className?: string;
}

const textVariants: Record<TextVariant, string> = {
  body: 'text-sm sm:text-base text-[var(--text-primary)] leading-relaxed',
  'body-sm': 'text-xs sm:text-sm text-[var(--text-secondary)] leading-normal',
  'body-lg': 'text-base sm:text-lg text-[var(--text-primary)] leading-relaxed font-normal',
  caption: 'text-xs text-[var(--text-tertiary)] leading-tight',
  overline: 'text-[11px] font-bold uppercase tracking-widest text-[var(--text-tertiary)]',
  muted: 'text-sm text-[var(--text-secondary)]',
  mono: 'font-mono text-xs text-[var(--text-secondary)] tabular-nums',
};

export const Text = React.forwardRef<HTMLElement, TextProps>(
  ({ as: Component = 'p', variant = 'body', className = '', children, ...props }, ref) => {
    const vClass = textVariants[variant] || textVariants.body;
    return (
      // @ts-expect-error Polymorphic element ref assignment
      <Component ref={ref} className={`${vClass} ${className}`.trim()} {...props}>
        {children}
      </Component>
    );
  }
);
Text.displayName = 'Text';

export interface MetricValueProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string | number;
  label?: string;
  subtext?: string;
  unit?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    text: string;
  };
  highlightColor?: string;
  className?: string;
}

const metricSizes = {
  sm: 'text-lg font-bold',
  md: 'text-2xl font-bold tracking-tight',
  lg: 'text-3xl sm:text-4xl font-extrabold tracking-tight',
  xl: 'text-4xl sm:text-5xl font-black tracking-tight',
};

export const MetricValue: React.FC<MetricValueProps> = ({
  value,
  label,
  subtext,
  unit,
  size = 'md',
  trend,
  highlightColor,
  className = '',
  ...props
}) => {
  return (
    <div className={`metric-value-container flex flex-col ${className}`.trim()} {...props}>
      {label && (
        <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-tertiary)] mb-1">
          {label}
        </span>
      )}
      <div className="flex items-baseline gap-1.5 flex-wrap">
        <span
          className={`font-mono tabular-nums leading-none ${metricSizes[size]}`}
          style={{ color: highlightColor || 'var(--text-primary)' }}
        >
          {value}
        </span>
        {unit && (
          <span className="text-xs sm:text-sm font-medium text-[var(--text-secondary)]">
            {unit}
          </span>
        )}
        {trend && (
          <span
            className={`inline-flex items-center text-xs font-semibold ml-2 px-1.5 py-0.5 rounded ${
              trend.direction === 'up'
                ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400'
                : trend.direction === 'down'
                ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
            }`}
          >
            {trend.text}
          </span>
        )}
      </div>
      {subtext && (
        <span className="text-xs text-[var(--text-secondary)] mt-1">
          {subtext}
        </span>
      )}
    </div>
  );
};

export const CodeChip: React.FC<React.HTMLAttributes<HTMLSpanElement>> = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <code
      className={`px-1.5 py-0.5 rounded text-xs font-mono bg-[var(--bg-elevated)] border border-[var(--border-subtle)] text-[var(--text-primary)] ${className}`.trim()}
      {...props}
    >
      {children}
    </code>
  );
};

export default Heading;
