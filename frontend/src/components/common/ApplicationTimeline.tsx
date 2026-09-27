import React from 'react';

export type ApplicationStage =
  | 'eligibility'
  | 'requirements'
  | 'preparation'
  | 'prepared'
  | 'consent'
  | 'reviewed'
  | 'submission'
  | 'submitted'
  | 'tracking'
  | 'gov_review'
  | 'decision'
  | 'recovery';

interface ApplicationTimelineProps {
  currentStage: ApplicationStage | string;
  isBlocked?: boolean;
  className?: string;
}

export function ApplicationTimeline({ currentStage, isBlocked = false, className = '' }: ApplicationTimelineProps) {
  // Section 22 Canonical Stages:
  // Eligibility → Requirements → Preparation → Consent → Submission/Handoff → Tracking → Decision → Recovery
  const canonicalStages = [
    { key: 'eligibility', label: 'Eligibility', sub: 'Policy Rule Matched', alt: [] },
    { key: 'requirements', label: 'Requirements', sub: 'Mandates Verified', alt: ['reviewed'] },
    { key: 'preparation', label: 'Preparation', sub: 'Dossier Compiled', alt: ['prepared'] },
    { key: 'consent', label: 'Consent', sub: 'Citizen Authorized', alt: [] },
    { key: 'submission', label: 'Submission', sub: 'Official Handoff', alt: ['submitted'] },
    { key: 'tracking', label: 'Tracking', sub: 'Statutory Queue', alt: ['gov_review'] },
    { key: 'decision', label: 'Decision', sub: 'Benefit Granted', alt: [] },
    { key: 'recovery', label: 'Recovery', sub: 'Continuity Safeguard', alt: [] },
  ];

  // Resolve current index based on canonical key or alternative aliases
  const normalizedKey = (currentStage || '').toLowerCase();
  const currentIndex = canonicalStages.findIndex(
    (s) => s.key === normalizedKey || s.alt.includes(normalizedKey)
  );
  const activeIdx = currentIndex >= 0 ? currentIndex : 2; // Default to preparation if unknown

  return (
    <div className={`app-timeline-container ${className}`}>
      <div className="app-timeline-track">
        {canonicalStages.map((stage, idx) => {
          const isPassed = idx < activeIdx;
          const isCurrent = idx === activeIdx;
          const isPending = idx > activeIdx;

          return (
            <div
              key={stage.key}
              className={`timeline-step ${isPassed ? 'passed' : ''} ${isCurrent ? 'current' : ''} ${
                isPending ? 'pending' : ''
              } ${isCurrent && isBlocked ? 'blocked' : ''}`}
            >
              <div className="timeline-node-wrap">
                <div className="timeline-node">
                  {isCurrent && isBlocked ? '!' : isPassed ? '✓' : idx + 1}
                  {isCurrent && <span className="timeline-node-halo" />}
                </div>
                {idx < canonicalStages.length - 1 && (
                  <div className={`timeline-connector ${isPassed ? 'passed' : ''}`}>
                    {isCurrent && <span className="connector-flow-dot" />}
                  </div>
                )}
              </div>
              <div className="timeline-labels">
                <strong className="timeline-step-title">{stage.label}</strong>
                <span className="timeline-step-sub">{stage.sub}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
