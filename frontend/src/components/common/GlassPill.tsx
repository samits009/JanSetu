import React from 'react';

export type GlassPillTone = 'gold' | 'emerald' | 'sky' | 'rose' | 'amber' | 'neutral';

interface GlassPillProps extends React.HTMLAttributes<HTMLSpanElement> {
  children: React.ReactNode;
  tone?: GlassPillTone;
  size?: 'sm' | 'md';
  icon?: React.ReactNode;
  active?: boolean;
  onClick?: () => void;
  className?: string;
}

export function GlassPill({
  children,
  tone = 'neutral',
  size = 'md',
  icon,
  active = false,
  onClick,
  className = '',
  ...rest
}: GlassPillProps) {
  const isInteractive = Boolean(onClick);

  return (
    <span
      className={`glass-pill glass-pill-${tone} glass-pill-${size} ${active ? 'active' : ''} ${
        isInteractive ? 'interactive' : ''
      } ${className}`}
      onClick={onClick}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      {...rest}
    >
      {icon && <span className="glass-pill-icon">{icon}</span>}
      <span className="glass-pill-text">{children}</span>
    </span>
  );
}
