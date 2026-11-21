import React from 'react';
import clsx from 'clsx';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'accent';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className,
  ...props
}) => {
  const variantStyles = {
    default: 'bg-nowcast-border text-nowcast-text',
    success: 'bg-nowcast-success/15 text-nowcast-success border border-nowcast-success/30',
    warning: 'bg-nowcast-warning/15 text-nowcast-warning border border-nowcast-warning/30',
    danger: 'bg-nowcast-danger/15 text-nowcast-danger border border-nowcast-danger/30',
    info: 'bg-nowcast-info/15 text-nowcast-info border border-nowcast-info/30',
    accent: 'bg-nowcast-accent/15 text-nowcast-accent border border-nowcast-accent/30',
  };

  const sizeStyles = {
    sm: 'text-[10px] px-1.5 py-0.5 rounded',
    md: 'text-xs px-2.5 py-1 rounded-md font-medium',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 leading-none tracking-wide font-sans',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
