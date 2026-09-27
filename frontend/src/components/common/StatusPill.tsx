import React from 'react';

export type StatusTone = 'green' | 'emerald' | 'amber' | 'gold' | 'blue' | 'sky' | 'red' | 'rose' | 'slate' | 'neutral';

interface StatusPillProps {
  children: React.ReactNode;
  tone?: StatusTone;
  icon?: React.ReactNode;
  pulse?: boolean;
  className?: string;
  size?: 'sm' | 'md';
}

export function StatusPill({
  children,
  tone = 'blue',
  icon,
  pulse = false,
  className = '',
  size = 'md',
}: StatusPillProps) {
  // Map aliases
  const resolvedTone =
    tone === 'emerald' ? 'green' :
    tone === 'gold' ? 'amber' :
    tone === 'sky' ? 'blue' :
    tone === 'rose' ? 'red' :
    tone === 'neutral' ? 'slate' : tone;

  return (
    <span className={`status-pill status-pill-${resolvedTone} status-pill-${size} ${className}`}>
      {pulse && <span className="status-pill-dot-pulse" aria-hidden="true" />}
      {!pulse && <span className="status-pill-dot" aria-hidden="true" />}
      {icon && <span className="status-pill-icon">{icon}</span>}
      <span className="status-pill-label">{children}</span>
    </span>
  );
}
