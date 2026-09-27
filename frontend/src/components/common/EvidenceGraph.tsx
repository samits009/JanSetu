import React from 'react';

export interface GraphNode {
  id: string;
  type: 'document' | 'evidence' | 'requirement' | 'scheme' | 'application';
  label: string;
  status: 'verified' | 'pending' | 'ready' | 'missing';
  subLabel?: string;
}

interface EvidenceGraphProps {
  nodes?: GraphNode[];
  className?: string;
}

export function EvidenceGraph({ nodes, className = '' }: EvidenceGraphProps) {
  // Default citizen-friendly demonstration chain if none provided
  const defaultNodes: GraphNode[] = [
    { id: '1', type: 'document', label: 'BOCW Passbook', status: 'verified', subLabel: 'Uploaded & Signed' },
    { id: '2', type: 'evidence', label: '90-Day Construction Work', status: 'verified', subLabel: 'Statutory Proof' },
    { id: '3', type: 'requirement', label: 'BOCW Registration Rule', status: 'verified', subLabel: 'Section 12 Verified' },
    { id: '4', type: 'scheme', label: 'Construction Worker Pension', status: 'ready', subLabel: 'Eligible ₹3,000/mo' },
    { id: '5', type: 'application', label: 'Direct Handoff Dossier', status: 'ready', subLabel: 'Ready for Consent' },
  ];

  const displayNodes = nodes && nodes.length > 0 ? nodes : defaultNodes;

  const typeIcons: Record<string, string> = {
    document: '📄',
    evidence: '🔍',
    requirement: '⚖️',
    scheme: '✦',
    application: '⚡',
  };

  const statusStyles: Record<string, { tone: string; text: string }> = {
    verified: { tone: 'green', text: 'Verified' },
    pending: { tone: 'amber', text: 'Reviewing' },
    ready: { tone: 'gold', text: 'Ready' },
    missing: { tone: 'red', text: 'Missing Proof' },
  };

  return (
    <div className={`evidence-graph-container ${className}`}>
      <div className="evidence-graph-header">
        <div>
          <span className="evidence-graph-badge">EVIDENCE-TO-WELFARE GRAPH</span>
          <h4 className="evidence-graph-title">Verified Path to Sovereign Entitlement</h4>
        </div>
        <span className="status-pill status-pill-green">5/5 Nodes Linked</span>
      </div>

      <div className="evidence-graph-flow">
        {displayNodes.map((node, index) => {
          const isLast = index === displayNodes.length - 1;
          const style = statusStyles[node.status] || statusStyles.verified;

          return (
            <React.Fragment key={node.id}>
              {/* Node Card */}
              <div className={`evidence-graph-node status-${node.status}`}>
                <div className="node-glow-ring" aria-hidden="true" />
                <div className="node-content">
                  <div className="node-icon-wrap">
                    <span className="node-type-icon">{typeIcons[node.type] || '●'}</span>
                  </div>
                  <div className="node-text">
                    <span className="node-type-badge">{node.type}</span>
                    <strong className="node-name">{node.label}</strong>
                    {node.subLabel && <small className="node-sub">{node.subLabel}</small>}
                  </div>
                  <span className={`node-status-chip chip-${style.tone}`}>
                    {style.text}
                  </span>
                </div>
              </div>

              {/* Glowing Curved Connector */}
              {!isLast && (
                <div className="evidence-graph-connector" aria-hidden="true">
                  <div className="connector-line">
                    <span className="connector-traveling-dot" />
                  </div>
                  <span className="connector-arrow">↓</span>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
