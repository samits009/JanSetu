import React from 'react';

export type ApplicationStage =
  | 'prepared'
  | 'reviewed'
  | 'consent'
  | 'submitted'
  | 'gov_review'
  | 'decision';

interface ApplicationTimelineProps {
  currentStage: ApplicationStage;
  className?: string;
}

export function ApplicationTimeline({ currentStage, className = '' }: ApplicationTimelineProps) {
  const stages: { key: ApplicationStage; label: string; sub: string }[] = [
    { key: 'prepared', label: 'Prepared', sub: 'Evidence Compiled' },
    { key: 'reviewed', label: 'Reviewed', sub: 'Rules Verified' },
    { key: 'consent', label: 'Consent', sub: 'Citizen Authorized' },
    { key: 'submitted', label: 'Handoff', sub: 'Official Portal' },
    { key: 'gov_review', label: 'Gov Review', sub: 'Department Ingestion' },
    { key: 'decision', label: 'Decision', sub: 'Benefit Granted' },
  ];

  const stageKeys = stages.map(s => s.key);
  const currentIndex = stageKeys.indexOf(currentStage);

  return (
    <div className={`app-timeline-container ${className}`}>
      <div className="app-timeline-track">
        {stages.map((stage, idx) => {
          const isPassed = idx < currentIndex;
          const isCurrent = idx === currentIndex;
          const isPending = idx > currentIndex;

          return (
            <div
              key={stage.key}
              className={`timeline-step ${isPassed ? 'passed' : ''} ${isCurrent ? 'current' : ''} ${
                isPending ? 'pending' : ''
              }`}
            >
              <div className="timeline-node-wrap">
                <div className="timeline-node">
                  {isPassed ? '✓' : idx + 1}
                  {isCurrent && <span className="timeline-node-halo" />}
                </div>
                {idx < stages.length - 1 && (
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
