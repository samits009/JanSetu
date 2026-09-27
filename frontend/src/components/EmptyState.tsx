import React from 'react';
import { GlassCard } from './common/GlassCard';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, icon = '📂', action }: EmptyStateProps) {
  return (
    <GlassCard variant="default" className="empty-state-glass" style={{ textAlign: 'center', padding: '40px 24px' }}>
      <div style={{ fontSize: '38px', marginBottom: '14px', filter: 'drop-shadow(0 0 12px rgba(245, 199, 124, 0.3))' }}>
        {icon}
      </div>
      <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', color: 'var(--text-primary)' }}>{title}</h3>
      <p style={{ margin: '0 auto 20px', maxWidth: '420px', color: 'var(--text-secondary)', fontSize: '13.5px' }}>
        {description}
      </p>
      {action && <div>{action}</div>}
    </GlassCard>
  );
}
