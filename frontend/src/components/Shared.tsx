import React from 'react';

export function StatusCard({ title, tone, subtitle, detail, action, onClick }: { title: string; tone: string; subtitle: string; detail?: string; action: string; onClick: () => void }) {
  return (
    <section className={`card status-card ${tone}`}>
      <div className="status-top">
        <h3>{title}</h3>
        <span className="status-chip">
          {tone === 'green' ? 'सुरक्षित' : tone === 'amber' ? 'कार्रवाई जरूरी' : tone === 'blue' ? 'नई योजना' : tone === 'red' ? 'Urgent' : 'प्रमाण बाकी'}
        </span>
      </div>
      <p>{subtitle}</p>
      {detail && (
        <div className="detail-row">
          <span>{detail}</span>
          <button onClick={onClick}>{action} →</button>
        </div>
      )}
    </section>
  );
}

export function Metric({ n, label, tone }: { n: number; label: string; tone: string }) {
  return (
    <div className={`metric card ${tone}`}>
      <strong>{n}</strong>
      <span>{label}</span>
    </div>
  );
}

import { useNavigate } from 'react-router-dom';

export function Page({ title, subtitle, back, children }: { title: string; subtitle?: string; back?: boolean; children: React.ReactNode }) {
  const navigate = useNavigate();
  return (
    <div className="stack page">
      {back && <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>}
      <div className="page-title">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {children}
    </div>
  );
}
