import React from 'react';

export type CardVariant = 'default' | 'elevated' | 'interactive' | 'accent' | 'glass' | 'subtle';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  padding?: CardPadding;
  className?: string;
  as?: React.ElementType;
}

const variantClasses: Record<CardVariant, string> = {
  default:
    'bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-[var(--shadow-card)]',
  elevated:
    'bg-[var(--bg-surface)] border border-[var(--border-subtle)] shadow-[var(--shadow-card-elevated)]',
  interactive:
    'bg-[var(--bg-surface)] border border-[var(--border-color)] shadow-[var(--shadow-card)] hover:border-[var(--color-primary)] hover:shadow-[var(--shadow-card-hover)] hover:-translate-y-0.5 transition-all duration-200 cursor-pointer',
  accent:
    'bg-[var(--bg-surface)] border border-[var(--border-color)] border-t-4 border-t-[var(--color-primary)] shadow-[var(--shadow-card)]',
  glass:
    'glass-card shadow-[var(--shadow-card)]',
  subtle:
    'bg-[var(--bg-elevated)] border border-[var(--border-subtle)]',
};

const paddingClasses: Record<CardPadding, string> = {
  none: 'p-0',
  sm: 'p-3 sm:p-4',
  md: 'p-4 sm:p-6',
  lg: 'p-6 sm:p-8',
};

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', className = '', as: Component = 'div', children, ...props }, ref) => {
    return (
      <Component
        ref={ref}
        className={`card-container rounded-xl transition-colors ${variantClasses[variant]} ${paddingClasses[padding]} ${className}`.trim()}
        {...props}
      >
        {children}
      </Component>
    );
  }
);
Card.displayName = 'Card';

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  bordered?: boolean;
}

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className = '', bordered = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`flex flex-col gap-1.5 ${bordered ? 'pb-4 mb-4 border-b border-[var(--border-color)]' : ''} ${className}`.trim()}
        {...props}
      >
        {children}
      </div>
    );
  }
);
CardHeader.displayName = 'CardHeader';

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

export const CardTitle = React.forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ as: Tag = 'h3', className = '', children, ...props }, ref) => {
    return (
      <Tag
        ref={ref}
        className={`text-lg font-semibold tracking-tight text-[var(--text-primary)] ${className}`.trim()}
        {...props}
      >
        {children}
      </Tag>
    );
  }
);
CardTitle.displayName = 'CardTitle';

export const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={`text-sm text-[var(--text-secondary)] leading-relaxed ${className}`.trim()}
        {...props}
      >
        {children}
      </p>
    );
  }
);
CardDescription.displayName = 'CardDescription';

export const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <div ref={ref} className={`card-content ${className}`.trim()} {...props}>
        {children}
      </div>
    );
  }
);
CardContent.displayName = 'CardContent';

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  bordered?: boolean;
}

export const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className = '', bordered = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`flex items-center gap-3 ${bordered ? 'pt-4 mt-4 border-t border-[var(--border-color)]' : ''} ${className}`.trim()}
        {...props}
      >
        {children}
      </div>
    );
  }
);
CardFooter.displayName = 'CardFooter';

export default Card;
