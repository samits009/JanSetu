import React from 'react';
import { GlassCard } from './common/GlassCard';

export function LoadingState({ message }: { message?: string }) {
  return (
    <GlassCard variant="default" className="loading-state-card" style={{ padding: '24px' }}>
      <div className="skeleton-line" style={{ width: '45%', height: '24px', marginBottom: '14px' }} />
      <div className="skeleton-line" style={{ width: '100%', height: '16px', marginBottom: '10px' }} />
      <div className="skeleton-line" style={{ width: '80%', height: '16px', marginBottom: '16px' }} />
      <div style={{ display: 'flex', gap: '10px' }}>
        <div className="skeleton-line" style={{ width: '90px', height: '32px', borderRadius: '9999px' }} />
        <div className="skeleton-line" style={{ width: '120px', height: '32px', borderRadius: '9999px' }} />
      </div>
      {message && (
        <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '14px', textAlign: 'center' }}>
          {message}
        </p>
      )}
    </GlassCard>
  );
}
