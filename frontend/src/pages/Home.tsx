import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useWelfareState } from '../hooks/useWelfareState';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { BenefitCard } from '../components/BenefitCard';
import {
  GlassCard,
  GlassButton,
  StatusPill,
  ProgressGlow,
  BridgePath,
  WelfareMetric,
} from '../components/common';

export function Home() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { language, t } = useI18n();
  const { welfareState, loading, error, refetch } = useWelfareState();

  if (loading) {
    return (
      <div className="stack">
        <LoadingState />
        <LoadingState />
      </div>
    );
  }

  if (error || !welfareState) {
    return (
      <div className="stack">
        <ErrorState error={error} onRetry={refetch} />
      </div>
    );
  }

  const active = welfareState.active_benefits.length;
  const action = welfareState.action_required.length;
  const newer = welfareState.new_opportunities.length;
  const risk = welfareState.at_risk.length;
  const needDocs = welfareState.document_gaps.length;

  const totalValue =
    welfareState.new_opportunities.reduce((s, b) => s + (b.amount || 0), 0) +
    welfareState.active_benefits.reduce((s, b) => s + (b.amount || 0), 0);

  const readinessScore = welfareState.evidence_readiness_score ?? 85;

  const citizenDisplayName =
    user?.name || welfareState.citizen_summary?.name || user?.email?.split('@')[0] || 'Citizen';

  return (
    <div className="stack">
      {/* 1. Hero: Greeting & Sovereign Welfare State */}
      <GlassCard variant="hero" className="home-hero-card">
        <div className="home-greeting-row">
          <div>
            <span className="status-pill status-pill-green status-pill-sm" style={{ marginBottom: 8 }}>
              ● {language === 'hi' ? 'नागरिक सुरक्षा सक्रिय' : 'Sovereign Protection Active'}
            </span>
            <h1 className="home-citizen-title">
              {language === 'hi' ? `नमस्ते, ${citizenDisplayName}` : `Good morning, ${citizenDisplayName}`}
            </h1>
            <p className="home-welfare-state-subtitle">
              {language === 'hi'
                ? 'आपकी कल्याणकारी स्थिति • Your welfare state'
                : 'Your welfare state'}
            </p>
          </div>

          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--gold-primary), #b45309)',
              color: '#ffffff',
              display: 'grid',
              placeItems: 'center',
              fontSize: 20,
              fontWeight: 800,
              boxShadow: '0 0 20px rgba(245, 199, 124, 0.4)',
              border: '2px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            ✓
          </div>
        </div>

        {/* Large Visual Welfare Summary */}
        <div className="welfare-summary-box">
          <div className="welfare-value-row">
            <div>
              <span style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
                {language === 'hi' ? 'कुल संभावित वार्षिक लाभ • Annual Entitlement' : 'Annual Welfare Potential'}
              </span>
              <div className="welfare-value-number">
                ₹{totalValue.toLocaleString('en-IN')}
                <small style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-secondary)', marginLeft: 6 }}>
                  / yr
                </small>
              </div>
            </div>

            <StatusPill tone="gold" size="sm">
              {active + action + newer + risk} {language === 'hi' ? 'योजनाएं' : 'Total Schemes'}
            </StatusPill>
          </div>

          {/* Signature Bridge Motif (Citizen -> Evidence -> Benefits -> Action) */}
          <BridgePath
            currentStage={action > 0 ? 'evidence' : 'benefits'}
            labels={{
              citizen: language === 'hi' ? 'नागरिक' : 'Citizen',
              evidence: language === 'hi' ? 'साक्ष्य' : 'Evidence',
              benefits: language === 'hi' ? 'योजनाएं' : 'Benefits',
              action: language === 'hi' ? 'कार्यवाही' : 'Action',
            }}
          />
        </div>
      </GlassCard>

      {/* 2. Action Needed Alert Banner */}
      {welfareState.action_required.length > 0 && (
        <GlassCard
          variant="alert"
          onClick={() => navigate('/benefits')}
          style={{ display: 'flex', alignItems: 'center', gap: 16, cursor: 'pointer' }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 14,
              background: 'rgba(245, 158, 11, 0.2)',
              border: '1px solid rgba(245, 158, 11, 0.4)',
              color: 'var(--gold-primary)',
              display: 'grid',
              placeItems: 'center',
              fontSize: 20,
              fontWeight: 'bold',
            }}
          >
            !
          </div>
          <div style={{ flex: 1 }}>
            <strong style={{ display: 'block', fontSize: 15, color: '#fef08a' }}>
              {welfareState.action_required.length}{' '}
              {language === 'hi' ? 'योजनाओं के लिए तुरंत साक्ष्य आवश्यक है' : 'Applications Need Your Attention'}
            </strong>
            <small style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
              {welfareState.action_required[0]?.title} — {welfareState.action_required[0]?.description}
            </small>
          </div>
          <span style={{ fontSize: 22, color: 'var(--gold-primary)' }}>›</span>
        </GlassCard>
      )}

      {/* 3. Evidence Readiness Section */}
      <GlassCard variant="default">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--sky-primary)' }}>
              {language === 'hi' ? 'साक्ष्य तत्परता • EVIDENCE READINESS' : 'EVIDENCE READINESS'}
            </span>
            <h3 style={{ margin: '2px 0 0', fontSize: 18 }}>
              {readinessScore}% {language === 'hi' ? 'सत्यापित दावे पुन: प्रयोज्य' : 'Verified Claims Reusable'}
            </h3>
          </div>
          <StatusPill tone={needDocs === 0 ? 'emerald' : 'amber'}>
            {needDocs === 0 ? '100% Ready' : `${needDocs} Gaps Remaining`}
          </StatusPill>
        </div>

        <ProgressGlow value={readinessScore} tone="gold" size="md" />

        <p style={{ margin: '12px 0 0', fontSize: 13, color: 'var(--text-secondary)' }}>
          {language === 'hi'
            ? 'आपका आधार, निर्माण श्रमिक पासबुक और राशन कार्ड सत्यापित हैं और आवेदन के लिए तैयार हैं।'
            : 'Your Aadhaar, worker certificates, and ration cards are deterministically verified and ready for consent-based handoff.'}
        </p>
      </GlassCard>

      {/* 4. Four Core Welfare Metrics Grid */}
      <div className="welfare-metrics-grid">
        <WelfareMetric
          label={language === 'hi' ? 'नए संभावित लाभ' : 'Potentially Relevant'}
          value={newer}
          subValue={language === 'hi' ? 'योजनाएं' : 'Schemes'}
          tone="gold"
          onClick={() => navigate('/benefits')}
        />
        <WelfareMetric
          label={language === 'hi' ? 'साक्ष्य तत्परता' : 'Evidence Readiness'}
          value={`${readinessScore}%`}
          subValue={language === 'hi' ? 'सत्यापित' : 'Verified'}
          tone="emerald"
          onClick={() => navigate('/documents')}
        />
        <WelfareMetric
          label={language === 'hi' ? 'ध्यान देने योग्य' : 'Needs Attention'}
          value={action}
          subValue={language === 'hi' ? 'कार्यवाही' : 'Actions'}
          tone="rose"
          onClick={() => navigate('/benefits')}
        />
        <WelfareMetric
          label={language === 'hi' ? 'सुरक्षित योजनाएं' : 'Protected Benefits'}
          value={active}
          subValue={language === 'hi' ? 'सक्रिय' : 'Active'}
          tone="blue"
          onClick={() => navigate('/benefits')}
        />
      </div>

      {/* 5. Potentially Relevant Benefits ("Why This May Apply") */}
      {welfareState.new_opportunities.length > 0 && (
        <section className="stack" style={{ gap: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ fontSize: 20 }}>
                {language === 'hi' ? 'नए संभावित लाभ' : 'Potentially Relevant Benefits'}
              </h2>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                {language === 'hi' ? 'पात्रता नियमों से सुमेलित' : 'Matched by deterministic policy rules'}
              </span>
            </div>
            <StatusPill tone="blue">{welfareState.new_opportunities.length} New</StatusPill>
          </div>

          {welfareState.new_opportunities.map((opp) => (
            <BenefitCard key={opp.id} benefit={opp} />
          ))}
        </section>
      )}

      {/* 6. Quick Action Drawer CTA */}
      <GlassCard variant="luminous" style={{ textAlign: 'center', padding: '24px 20px' }}>
        <h3 style={{ fontSize: 18, marginBottom: 6 }}>
          {language === 'hi' ? 'जनसेतु स्वायत्त सहायक' : 'Autonomous JanSetu Action'}
        </h3>
        <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', maxWidth: 440, margin: '0 auto 16px' }}>
          {language === 'hi'
            ? 'जनसेतु आपके सत्यापित दस्तावेज़ों से आवेदन तैयार रखता है। आपके अनुमोदन के बाद ही पोर्टल में सबमिट होता है।'
            : 'JanSetu compiles your verified proofs into official dossiers. Nothing is sent without your explicit sovereign consent.'}
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <GlassButton
            variant="primary"
            size="md"
            fullWidth={false}
            onClick={() => navigate('/applications')}
          >
            {language === 'hi' ? 'आवेदन की समीक्षा करें →' : 'Review Applications →'}
          </GlassButton>
        </div>
      </GlassCard>
    </div>
  );
}
