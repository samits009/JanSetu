import React from 'react';

interface BridgePathProps {
  currentStage?: 'citizen' | 'evidence' | 'benefits' | 'action';
  className?: string;
  labels?: {
    citizen?: string;
    evidence?: string;
    benefits?: string;
    action?: string;
  };
}

export function BridgePath({
  currentStage = 'evidence',
  className = '',
  labels = {
    citizen: 'Citizen',
    evidence: 'Evidence',
    benefits: 'Benefits',
    action: 'Action',
  },
}: BridgePathProps) {
  const stages = [
    { key: 'citizen', label: labels.citizen || 'Citizen', icon: '👤' },
    { key: 'evidence', label: labels.evidence || 'Evidence', icon: '📄' },
    { key: 'benefits', label: labels.benefits || 'Benefits', icon: '✦' },
    { key: 'action', label: labels.action || 'Action', icon: '⚡' },
  ];

  const stageIndex = stages.findIndex(s => s.key === currentStage);

  return (
    <div className={`bridge-path-container ${className}`}>
      {/* SVG Curved Glowing Arc with Traveling Light */}
      <svg className="bridge-path-svg" viewBox="0 0 600 70" preserveAspectRatio="none">
        <defs>
          <linearGradient id="bridgeFlowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.4" />
            <stop offset="35%" stopColor="#10B981" stopOpacity="0.6" />
            <stop offset="70%" stopColor="#F5C77C" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#F59E0B" stopOpacity="1" />
          </linearGradient>

          <filter id="bridgePathGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="glow" />
            <feMerge>
              <feMergeNode in="glow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Ambient Subtle Track */}
        <path
          d="M 40,35 Q 170,10 300,35 T 560,35"
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth="3"
        />

        {/* Glowing Connected Flow Line */}
        <path
          d="M 40,35 Q 170,10 300,35 T 560,35"
          fill="none"
          stroke="url(#bridgeFlowGrad)"
          strokeWidth="2.5"
          filter="url(#bridgePathGlow)"
        />

        {/* Traveling Luminous Pulse */}
        <path
          d="M 40,35 Q 170,10 300,35 T 560,35"
          fill="none"
          stroke="#FFFBEB"
          strokeWidth="3.5"
          strokeDasharray="18 180"
          className="traveling-light"
        />
      </svg>

      {/* Connected Milestone Nodes */}
      <div className="bridge-nodes-row">
        {stages.map((stage, idx) => {
          const isPassed = idx < stageIndex;
          const isCurrent = idx === stageIndex;

          return (
            <div
              key={stage.key}
              className={`bridge-node-item ${isPassed ? 'passed' : ''} ${isCurrent ? 'current' : ''}`}
            >
              <div className="bridge-node-circle">
                <span className="node-icon">{stage.icon}</span>
                {isCurrent && <span className="node-pulse-ring" />}
              </div>
              <span className="bridge-node-label">{stage.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
