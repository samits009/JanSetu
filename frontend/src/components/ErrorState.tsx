import React from 'react';
import { ApiError } from '../services/apiClient';
import { GlassCard } from './common/GlassCard';
import { GlassButton } from './common/GlassButton';

interface ErrorStateProps {
  error: Error | ApiError | null;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  if (!error) return null;

  const isApiError = error instanceof ApiError;
  const message = error.message || 'An unexpected error occurred while communicating with JanSetu services.';
  const retryable = isApiError ? error.retryable : true;

  return (
    <GlassCard variant="alert" className="error-state-glass" style={{ margin: '12px 0', padding: '18px 20px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '12px',
            background: 'rgba(244, 63, 94, 0.2)',
            border: '1px solid rgba(244, 63, 94, 0.4)',
            color: '#fb7185',
            display: 'grid',
            placeItems: 'center',
            fontSize: '18px',
            fontWeight: 'bold',
            flexShrink: 0,
          }}
        >
          !
        </div>

        <div style={{ flex: 1 }}>
          <strong style={{ display: 'block', fontSize: '14.5px', color: '#fecdd3', marginBottom: '3px' }}>
            Action Required / Notice
          </strong>
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)' }}>
            {message}
          </p>
        </div>

        {retryable && onRetry && (
          <GlassButton
            type="button"
            variant="danger"
            size="sm"
            fullWidth={false}
            onClick={onRetry}
            style={{ flexShrink: 0 }}
          >
            Retry
          </GlassButton>
        )}
      </div>
    </GlassCard>
  );
}
