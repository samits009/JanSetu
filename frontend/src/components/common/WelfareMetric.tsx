import React from 'react';

interface WelfareMetricProps {
  label: string;
  value: string | number;
  subValue?: string;
  tone?: 'gold' | 'emerald' | 'blue' | 'rose' | 'slate';
  icon?: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export function WelfareMetric({
  label,
  value,
  subValue,
  tone = 'gold',
  icon,
  onClick,
  className = '',
}: WelfareMetricProps) {
  return (
    <div
      className={`welfare-metric-card welfare-metric-tone-${tone} ${onClick ? 'interactive' : ''} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="metric-glow-orb" aria-hidden="true" />
      <div className="metric-header">
        <span className="metric-label">{label}</span>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <div className="metric-value-row">
        <span className="metric-number">{value}</span>
        {subValue && <span className="metric-sub">{subValue}</span>}
      </div>
    </div>
  );
}
