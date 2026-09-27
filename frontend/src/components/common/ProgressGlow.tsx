import React from 'react';

interface ProgressGlowProps {
  value: number; // 0 - 100
  tone?: 'gold' | 'emerald' | 'blue';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
  className?: string;
}

export function ProgressGlow({
  value,
  tone = 'gold',
  size = 'md',
  showLabel = false,
  label,
  className = '',
}: ProgressGlowProps) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div className={`progress-glow-container ${className}`}>
      {showLabel && (
        <div className="progress-glow-header">
          <span className="progress-glow-label">{label || 'Readiness'}</span>
          <span className={`progress-glow-percent text-${tone}`}>{clamped}%</span>
        </div>
      )}
      <div className={`progress-glow-track progress-glow-${size}`}>
        <div
          className={`progress-glow-fill progress-glow-tone-${tone}`}
          style={{ width: `${clamped}%` }}
        >
          <span className="progress-glow-tip" />
        </div>
      </div>
    </div>
  );
}
