import React from 'react';
import { GlassCard } from './GlassCard';
import { StatusPill } from './StatusPill';

export interface DocumentCardData {
  id: string;
  document_type: string;
  file_name?: string;
  verification_status: 'VERIFIED' | 'PENDING' | 'REJECTED' | string;
  created_at?: string;
  extracted_data?: Record<string, any>;
  linked_schemes_count?: number;
}

interface DocumentCardProps {
  document: DocumentCardData;
  onClick?: () => void;
  className?: string;
}

const DOC_TYPE_METAS: Record<string, { label: string; icon: string; source: string }> = {
  BOCW_CARD: {
    label: 'BOCW Worker Passbook',
    icon: '🏗️',
    source: 'State Building & Construction Workers Board',
  },
  AADHAAR: {
    label: 'Aadhaar Identity Card',
    icon: '🆔',
    source: 'UIDAI Sovereign Identity Repository',
  },
  RATION_CARD: {
    label: 'National Food Security (NFSA) Ration Card',
    icon: '🌾',
    source: 'Department of Food & Public Distribution',
  },
  GENERAL: {
    label: 'Statutory Verification Document',
    icon: '📄',
    source: 'Self-Attested / Verified Record',
  },
};

export function DocumentCard({ document, onClick, className = '' }: DocumentCardProps) {
  const meta = DOC_TYPE_METAS[document.document_type] || {
    label: document.document_type.replace(/_/g, ' '),
    icon: '📄',
    source: 'Official Record',
  };

  const isVerified = document.verification_status === 'VERIFIED';
  const isPending = document.verification_status === 'PENDING';
  const claimsCount = document.extracted_data ? Object.keys(document.extracted_data).length : 0;

  const dateFormatted = document.created_at
    ? new Date(document.created_at).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
    : 'Verified recently';

  return (
    <GlassCard
      variant="default"
      className={`document-card-glass ${onClick ? 'interactive' : ''} ${className}`}
      onClick={onClick}
    >
      <div className="doc-card-inner">
        {/* Document Icon / Thumbnail Capsule */}
        <div className={`doc-card-thumb ${isVerified ? 'verified' : ''}`}>
          <span className="doc-thumb-icon">{meta.icon}</span>
        </div>

        {/* Main Details */}
        <div className="doc-card-body">
          <div className="doc-card-header-row">
            <h4 className="doc-card-title">{meta.label}</h4>
            <StatusPill
              tone={isVerified ? 'emerald' : isPending ? 'amber' : 'rose'}
              size="sm"
            >
              {document.verification_status}
            </StatusPill>
          </div>

          <div className="doc-card-meta-row">
            <span className="doc-card-source">🏛️ {meta.source}</span>
            <span className="doc-meta-divider">•</span>
            <span className="doc-card-date">Uploaded: {dateFormatted}</span>
          </div>

          {/* Extracted Evidence Chips */}
          {claimsCount > 0 && (
            <div className="doc-card-claims-row">
              <span className="claims-count-badge">
                ✓ {claimsCount} Statutory Evidence Claims Extracted
              </span>
            </div>
          )}
        </div>

        {/* Right Arrow / Action Indicator */}
        <div className="doc-card-arrow" aria-hidden="true">
          <span>›</span>
        </div>
      </div>
    </GlassCard>
  );
}
