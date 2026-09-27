import React from 'react';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'hero' | 'luminous' | 'alert' | 'subtle';
  className?: string;
}

export function GlassCard({
  children,
  variant = 'default',
  className = '',
  onClick,
  style,
  id,
  ...rest
}: GlassCardProps) {
  return (
    <div
      id={id}
      className={`glass-card glass-card-${variant} ${className} ${onClick ? 'glass-card-interactive' : ''}`}
      onClick={onClick}
      style={style}
      {...rest}
    >
      {/* Subtle Inner Highlight Flare */}
      <div className="glass-card-glow-edge" aria-hidden="true" />
      {children}
    </div>
  );
}
