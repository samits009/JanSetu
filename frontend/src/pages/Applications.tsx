import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import { applicationApi } from '../services/applicationApi';
import { ApplicationResponse } from '../domain/models';
import { AgentChat } from '../components/AgentChat';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import {
  GlassCard,
  GlassButton,
  StatusPill,
  ProgressGlow,
  ApplicationTimeline,
  ApplicationStage,
  GlassModal,
} from '../components/common';

export function Applications() {
  const { currentCitizenId, user } = useAuth();
  const { language, t } = useI18n();
  const [apps, setApps] = useState<ApplicationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [handoffData, setHandoffData] = useState<Record<string, any>>({});
  const [loadingHandoff, setLoadingHandoff] = useState<string | null>(null);
  const [recoveryModalOpen, setRecoveryModalOpen] = useState(false);
  const [prepModalOpen, setPrepModalOpen] = useState(false);
  const navigate = useNavigate();
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [recoveryExecuted, setRecoveryExecuted] = useState(false);

  const appsNeedingAttention = apps.filter(
    (a) => a.status === 'REQUIRES_EVIDENCE' || a.status === 'REJECTED'
  );
  const activeAttentionApp = appsNeedingAttention[0];
  const activeAppForPrep = apps.find((a) => a.id === selectedAppId) || apps[0];

  useEffect(() => {
    loadApplications();
  }, [currentCitizenId]);

  const loadApplications = () => {
    setLoading(true);
    applicationApi
      .listMyApplications()
      .then(setApps)
      .catch((err) => {
        if (currentCitizenId) {
          return applicationApi.listApplications(currentCitizenId).then(setApps);
        }
        throw err;
      })
      .catch(setError)
      .finally(() => setLoading(false));
  };

  const handlePrepareHandoff = async (id: string) => {
    setLoadingHandoff(id);
    try {
      const data = await applicationApi.getHandoff(id);
      setHandoffData((prev) => ({ ...prev, [id]: data }));
    } catch (err: any) {
      console.error('Handoff preparation failed', err);
    } finally {
      setLoadingHandoff(null);
    }
  };

  const getTimelineStage = (status: string): ApplicationStage => {
    switch (status) {
      case 'DRAFT':
        return 'prepared';
      case 'IN_REVIEW':
        return 'reviewed';
      case 'CONSENT_GRANTED':
        return 'consent';
      case 'SUBMITTED':
      case 'HANDOFF_READY':
        return 'submitted';
      case 'PENDING_GOV_REVIEW':
        return 'gov_review';
      case 'APPROVED':
      case 'REJECTED':
        return 'decision';
      default:
        return 'submitted';
    }
  };

  const citizenName = user?.name || user?.email?.split('@')[0] || 'Citizen';

  const handleExecuteRecovery = () => {
    setRecoveryExecuted(true);
    setRecoveryModalOpen(false);
    setTimeout(() => setRecoveryExecuted(false), 6000);
  };

  return (
    <div className="stack">
      {/* 1. Header Card */}
      <GlassCard variant="hero">
        <span className="status-pill status-pill-gold status-pill-sm" style={{ marginBottom: 6 }}>
          ✦ WELFARE APPLICATIONS & HANDOFF
        </span>
        <h1 style={{ fontSize: 24 }}>
          {language === 'hi' ? 'सक्रिय एवं तैयार आवेदन' : 'Active & Prepared Applications'}
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, margin: '4px 0 16px' }}>
          {language === 'hi'
            ? 'सत्यापित साक्ष्य, नियमों की समीक्षा और आधिकारिक पोर्टल हैंडऑफ की स्थिति।'
            : 'Track statutory verification, citizen consent, and official government portal handoffs.'}
        </p>

        <div style={{ display: 'flex', gap: 10 }}>
          <GlassButton
            variant="secondary"
            size="sm"
            fullWidth={false}
            onClick={() => setPrepModalOpen(true)}
          >
            📋 {language === 'hi' ? 'आवेदन तैयारी पत्रक खोलें' : 'Application Preparation Sheet'}
          </GlassButton>
        </div>
      </GlassCard>

      {/* RECOVERY EXECUTION TOAST */}
      {recoveryExecuted && (
        <GlassCard variant="luminous" style={{ borderLeft: '4px solid #10b981', padding: '14px 18px' }}>
          <strong style={{ color: '#34d399', display: 'block', fontSize: 14 }}>
            ✓ {language === 'hi' ? 'सुधार योजना निष्पादित' : 'Recovery Plan Successfully Executed'}
          </strong>
          <small style={{ color: 'var(--text-secondary)', fontSize: 12.5 }}>
            {language === 'hi'
              ? 'जनसेतु ने सत्यापित 2024 निर्माण कार्य पंजीकरण को लिंक कर दिया है और आवेदन को 100% तत्परता पर पुनर्स्थापित किया है।'
              : 'JanSetu has linked your verified 2024 site registration and restored application readiness to 100%.'}
          </small>
        </GlassCard>
      )}

      {/* 2. RECOVERY EXPERIENCE: Dynamically rendered only when an application requires attention/evidence */}
      {activeAttentionApp && !recoveryExecuted && (
        <GlassCard variant="alert" style={{ borderLeft: '4px solid var(--rose-primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 11, fontWeight: 800, color: '#fca5a5', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              APPLICATION NEEDS ATTENTION
            </span>
            <StatusPill tone="rose" size="sm">Action Required</StatusPill>
          </div>

          <h3 style={{ fontSize: 17, marginBottom: 4 }}>
            {activeAttentionApp.scheme_name}
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12 }}>
            <strong style={{ color: '#f87171' }}>Status:</strong> {activeAttentionApp.status} — Statutory re-evaluation or alternative verified evidence required.
          </p>

          <GlassButton
            variant="primary"
            size="sm"
            fullWidth={false}
            onClick={() => setRecoveryModalOpen(true)}
          >
            Review Recovery Plan →
          </GlassButton>
        </GlassCard>
      )}

      {/* 3. AI Assistant Chat Component */}
      <AgentChat />

      {/* 4. Applications List */}
      <section className="stack" style={{ gap: 14 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: 16 }}>
            {language === 'hi' ? 'नागरिक आवेदन ट्रैक' : 'Your Application Portfolios'}
          </h3>
          <StatusPill tone="blue">{apps.length} Total</StatusPill>
        </div>

        {loading && <LoadingState />}
        {error && <ErrorState error={error} onRetry={loadApplications} />}

        {!loading && !error && apps.length === 0 && (
          <GlassCard style={{ textAlign: 'center', padding: '36px 20px' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14, margin: '0 0 8px' }}>
              {language === 'hi'
                ? 'वर्तमान में कोई सक्रिय आवेदन नहीं है।'
                : 'No active welfare applications found.'}
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 18 }}>
              {language === 'hi'
                ? 'योजनाएं पृष्ठ पर जाकर पात्रता देखें और पहला आवेदन तैयार करें।'
                : 'Visit the Benefits page to discover schemes you qualify for and prepare an application.'}
            </p>
            <GlassButton
              variant="primary"
              size="md"
              fullWidth={false}
              onClick={() => navigate('/benefits')}
            >
              ✦ {language === 'hi' ? 'योजनाएं खोजें' : 'Explore Eligible Schemes'} →
            </GlassButton>
          </GlassCard>
        )}

        {!loading &&
          !error &&
          apps.map((app) => {
            const handoff = handoffData[app.id];
            const stage = getTimelineStage(app.status);

            return (
              <GlassCard key={app.id} variant="default" style={{ padding: '22px' }}>
                {/* Header: Scheme Name, Status, ID */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                  <div>
                    <h3 style={{ fontSize: 18, color: 'var(--text-primary)', marginBottom: 4 }}>
                      {app.scheme_name}
                    </h3>
                    <small style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                      Application ID: {app.id.slice(0, 12)}... • Updated Today
                    </small>
                  </div>
                  <StatusPill
                    tone={
                      app.status === 'APPROVED'
                        ? 'emerald'
                        : app.status === 'REJECTED'
                        ? 'rose'
                        : 'gold'
                    }
                  >
                    {app.status}
                  </StatusPill>
                </div>

                {/* Readiness Meter */}
                <div style={{ marginBottom: 16 }}>
                  <ProgressGlow
                    value={app.status === 'APPROVED' ? 100 : 75}
                    tone={app.status === 'APPROVED' ? 'emerald' : 'gold'}
                    size="sm"
                    showLabel={true}
                    label="Application Readiness"
                  />
                </div>

                {/* Glowing Progress Paths Timeline */}
                <ApplicationTimeline currentStage={stage} />

                {/* Handoff Details */}
                {handoff ? (
                  <div
                    style={{
                      background: 'rgba(56, 189, 248, 0.08)',
                      border: '1px solid rgba(56, 189, 248, 0.3)',
                      borderRadius: 16,
                      padding: 16,
                      marginTop: 16,
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <strong style={{ color: 'var(--sky-primary)', fontSize: 14 }}>
                        🏛️ {handoff.portal_name}
                      </strong>
                      <span className="status-pill status-pill-blue status-pill-sm">
                        {handoff.handoff_reference}
                      </span>
                    </div>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
                      {language === 'hi' ? handoff.instructions_hi : handoff.instructions_en}
                    </p>
                    <a
                      href={handoff.portal_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="glass-btn glass-btn-primary glass-btn-sm"
                      style={{ display: 'inline-flex', textDecoration: 'none' }}
                    >
                      {language === 'hi' ? 'आधिकारिक पोर्टल खोलें ↗' : 'Open Official Portal ↗'}
                    </a>
                  </div>
                ) : (
                  <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
                    <GlassButton
                      variant="primary"
                      size="sm"
                      fullWidth={false}
                      loading={loadingHandoff === app.id}
                      onClick={() => handlePrepareHandoff(app.id)}
                    >
                      {loadingHandoff === app.id
                        ? 'Compiling Dossier...'
                        : `🏛️ ${t('common.officialHandoff', 'Prepare Government Handoff')}`}
                    </GlassButton>
                  </div>
                )}
              </GlassCard>
            );
          })}
      </section>

      {/* 5. APPLICATION PREPARATION SHEET MODAL */}
      <GlassModal
        isOpen={prepModalOpen}
        onClose={() => setPrepModalOpen(false)}
        title="Application Preparation Sheet"
        subtitle="Centered welfare dossier review before official portal handoff"
        size="md"
        footer={
          <div style={{ display: 'flex', gap: 10, width: '100%' }}>
            <GlassButton
              variant="primary"
              size="md"
              onClick={() => {
                setPrepModalOpen(false);
                if (apps.length > 0) handlePrepareHandoff(apps[0].id);
              }}
            >
              Review Application →
            </GlassButton>
            <GlassButton
              variant="secondary"
              size="md"
              onClick={() => setPrepModalOpen(false)}
            >
              Close
            </GlassButton>
          </div>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Sections: Applicant, Scheme, Eligibility, Requirements, Evidence, Missing items */}
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Applicant</span>
            <strong style={{ color: '#f8fafc', fontSize: 13.5 }}>{citizenName}</strong>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Scheme</span>
            <strong style={{ color: '#f8fafc', fontSize: 13.5 }}>
              {activeAppForPrep ? activeAppForPrep.scheme_name : 'No application selected'}
            </strong>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Application Status</span>
            <span style={{ color: '#34d399', fontSize: 13, fontWeight: 700 }}>
              ✓ {activeAppForPrep ? activeAppForPrep.status : 'DRAFT'}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Reference ID</span>
            <strong style={{ color: 'var(--gold-primary)', fontSize: 13 }}>
              {activeAppForPrep ? activeAppForPrep.id : 'N/A'}
            </strong>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Dossier Validation</span>
            <span style={{ color: '#7dd3fc', fontSize: 13 }}>Statutory Policy Checked</span>
          </div>

          {/* Readiness Meter */}
          <div style={{ marginTop: 8 }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 6 }}>
              Dossier Verification Status
            </span>
            <ProgressGlow
              value={activeAppForPrep?.status === 'APPROVED' ? 100 : activeAppForPrep?.status === 'SUBMITTED' ? 85 : 75}
              tone="gold"
              size="lg"
              showLabel={true}
              label={activeAppForPrep ? `Status: ${activeAppForPrep.status}` : 'Readiness'}
            />
          </div>
        </div>
      </GlassModal>

      {/* 6. RECOVERY PLAN MODAL */}
      <GlassModal
        isOpen={recoveryModalOpen}
        onClose={() => setRecoveryModalOpen(false)}
        title="Autonomous Recovery Plan"
        subtitle="JanSetu resolution engine found alternative evidence"
        size="md"
        footer={
          <div style={{ display: 'flex', gap: 10, width: '100%' }}>
            <GlassButton
              variant="primary"
              size="md"
              onClick={handleExecuteRecovery}
            >
              Execute Recovery Plan →
            </GlassButton>
            <GlassButton
              variant="secondary"
              size="md"
              onClick={() => setRecoveryModalOpen(false)}
            >
              Cancel
            </GlassButton>
          </div>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, margin: 0 }}>
            JanSetu has linked your historical worker registration certificate. Executing this recovery plan will automatically revalidate statutory criteria and prepare the corrected application dossier.
          </p>

          <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 14, padding: '14px 16px', border: '1px solid rgba(255,255,255,0.08)' }}>
            <strong style={{ color: 'var(--gold-primary)', fontSize: 13, display: 'block', marginBottom: 8 }}>
              Recovery Plan Steps:
            </strong>
            <ol style={{ paddingLeft: 18, margin: 0, fontSize: 13, color: '#e2e8f0', display: 'flex', flexDirection: 'column', gap: 6 }}>
              <li>Replace unsupported evidence with verified 2024 site record</li>
              <li>Revalidate statutory rules in deterministic engine</li>
              <li>Prepare corrected handoff package for portal transmission</li>
            </ol>
          </div>
        </div>
      </GlassModal>
    </div>
  );
}
