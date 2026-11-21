import React from 'react';
import clsx from 'clsx';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'active' | 'danger';
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  className,
  ...props
}) => {
  const variantStyles = {
    default: 'bg-nowcast-sidebar border-nowcast-card',
    active: 'bg-nowcast-sidebar border-nowcast-accent/40 shadow-[0_0_15px_rgba(204,255,0,0.1)]',
    danger: 'bg-nowcast-sidebar border-nowcast-danger/40 shadow-[0_0_15px_rgba(255,71,87,0.1)]',
  };

  return (
    <div
      className={clsx(
        'rounded-xl border p-4 text-nowcast-text transition-all duration-200',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
