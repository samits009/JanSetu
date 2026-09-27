import React from 'react';
import { StatusPill } from './StatusPill';

export type EvidenceNodeType = 'document' | 'evidence' | 'requirement' | 'scheme' | 'application';
export type EvidenceNodeStatus = 'verified' | 'pending' | 'ready' | 'missing';

export interface EvidenceNodeProps {
  id?: string;
  type: EvidenceNodeType;
  label: string;
  subLabel?: string;
  status: EvidenceNodeStatus;
  value?: string;
  onClick?: () => void;
  className?: string;
}

const TYPE_ICONS: Record<EvidenceNodeType, string> = {
  document: '📄',
  evidence: '🔍',
  requirement: '⚖️',
  scheme: '✦',
  application: '⚡',
};

const STATUS_TONES: Record<EvidenceNodeStatus, 'emerald' | 'amber' | 'gold' | 'rose'> = {
  verified: 'emerald',
  pending: 'amber',
  ready: 'gold',
  missing: 'rose',
};

const STATUS_LABELS: Record<EvidenceNodeStatus, string> = {
  verified: 'Verified',
  pending: 'Reviewing',
  ready: 'Ready',
  missing: 'Missing Proof',
};

export function EvidenceNode({
  type,
  label,
  subLabel,
  status,
  value,
  onClick,
  className = '',
}: EvidenceNodeProps) {
  const tone = STATUS_TONES[status] || 'emerald';
  const statusLabel = STATUS_LABELS[status] || 'Verified';

  return (
    <div
      className={`evidence-node-item status-${status} ${onClick ? 'interactive' : ''} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="evidence-node-glow" aria-hidden="true" />

      <div className="evidence-node-icon-box">
        <span className="evidence-node-type-icon">{TYPE_ICONS[type] || '●'}</span>
      </div>

      <div className="evidence-node-details">
        <div className="evidence-node-type-pill">
          <span>{type.toUpperCase()}</span>
        </div>
        <strong className="evidence-node-title">{label}</strong>
        {subLabel && <span className="evidence-node-sub">{subLabel}</span>}
        {value && <span className="evidence-node-value">{value}</span>}
      </div>

      <div className="evidence-node-status-badge">
        <StatusPill tone={tone} size="sm">
          {statusLabel}
        </StatusPill>
      </div>
    </div>
  );
}
