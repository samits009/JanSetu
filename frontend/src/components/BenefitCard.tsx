import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BenefitSummary, NewOpportunity } from '../domain/models';
import { GlassCard, StatusPill, ProgressGlow, GlassButton } from './common';

export function BenefitCard({ benefit }: { benefit: BenefitSummary | NewOpportunity }) {
  const navigate = useNavigate();

  const isSummary = 'status' in benefit;
  const status = isSummary ? (benefit as BenefitSummary).status : 'POTENTIALLY_RELEVANT';
  const opp = !isSummary ? (benefit as NewOpportunity) : null;
  const readiness = opp?.readiness_percentage ?? 100;

  return (
    <GlassCard variant="default" className="benefit-card-glass" style={{ padding: '20px 22px' }}>
      {/* Top Header Pill & Value */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <StatusPill tone={status === 'ACTIVE' ? 'emerald' : 'gold'}>
          {status === 'ACTIVE' ? 'ACTIVE BENEFIT' : 'POTENTIALLY RELEVANT'}
        </StatusPill>

        {benefit.amount ? (
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: 18, fontWeight: 800, color: 'var(--gold-primary)', fontFamily: 'var(--font-display)' }}>
              ₹{benefit.amount.toLocaleString('en-IN')}
            </span>
            <small style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block' }}>/ year</small>
          </div>
        ) : (
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Statutory Support</span>
        )}
      </div>

      {/* Scheme Title & Category */}
      <h3 style={{ fontSize: 18, marginBottom: 4, color: 'var(--text-primary)' }}>
        {benefit.scheme_name}
      </h3>
      <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 14 }}>
        {opp?.category || 'Central & State Social Security Scheme'}
      </p>

      {/* Why This May Apply Preview */}
      {opp && opp.why_it_applies && opp.why_it_applies.length > 0 && (
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 14,
            padding: '12px 14px',
            marginBottom: 14,
          }}
        >
          <strong style={{ fontSize: 11.5, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--gold-primary)', display: 'block', marginBottom: 6 }}>
            ✦ WHY THIS MAY APPLY:
          </strong>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 5 }}>
            {opp.why_it_applies.slice(0, 3).map((reason, idx) => (
              <li key={idx} style={{ fontSize: 12.5, color: '#e2e8f0', display: 'flex', alignItems: 'center', gap: 7 }}>
                <span style={{ color: '#34d399', fontWeight: 'bold' }}>✓</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Readiness Bar */}
      <div style={{ marginBottom: 16 }}>
        <ProgressGlow
          value={readiness}
          tone={readiness === 100 ? 'emerald' : 'gold'}
          size="sm"
          showLabel={true}
          label="Evidence Readiness"
        />
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
        <button
          type="button"
          onClick={() => navigate(`/benefits/${benefit.id}`)}
          style={{
            background: 'rgba(255, 255, 255, 0.08)',
            border: '1px solid var(--glass-border)',
            borderRadius: 9999,
            padding: '8px 18px',
            color: 'var(--text-primary)',
            fontSize: 13,
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
        >
          Explore Benefit →
        </button>

        {!isSummary && (
          <button
            type="button"
            onClick={() => navigate('/applications')}
            style={{
              background: 'linear-gradient(135deg, var(--gold-light), var(--gold-primary))',
              border: '1px solid rgba(255, 255, 255, 0.4)',
              borderRadius: 9999,
              padding: '8px 18px',
              color: 'var(--gold-text-on-btn)',
              fontSize: 13,
              fontWeight: 700,
              cursor: 'pointer',
              boxShadow: '0 0 15px rgba(245, 199, 124, 0.35)',
            }}
          >
            Apply Now
          </button>
        )}
      </div>
    </GlassCard>
  );
}
