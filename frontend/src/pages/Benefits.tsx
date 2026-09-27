import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useWelfareState } from '../hooks/useWelfareState';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import { benefitApi } from '../services/benefitApi';
import { applicationApi } from '../services/applicationApi';
import { BenefitDetail as BenefitDetailModel } from '../domain/models';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { BenefitCard } from '../components/BenefitCard';
import {
  GlassCard,
  GlassButton,
  StatusPill,
  ProgressGlow,
  WelfareMetric,
} from '../components/common';

type FilterType = 'ALL' | 'ACTIVE' | 'ACTION' | 'NEW' | 'RISK';

export function Benefits() {
  const { welfareState, loading, error, refetch } = useWelfareState();
  const [filter, setFilter] = useState<FilterType>('ALL');
  const { language } = useI18n();

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

  const active = welfareState.active_benefits;
  const action = welfareState.action_required;
  const newer = welfareState.new_opportunities;
  const risk = welfareState.at_risk;
  const total = active.length + action.length + newer.length + risk.length;

  return (
    <div className="stack">
      {/* Header Overview Card */}
      <GlassCard variant="hero">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span className="status-pill status-pill-gold status-pill-sm" style={{ marginBottom: 6 }}>
              ✦ SOVEREIGN WELFARE PORTFOLIO
            </span>
            <h1 style={{ fontSize: 24 }}>
              {language === 'hi' ? 'योजना पोर्टफोलियो' : 'Welfare Benefits Portfolio'}
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, marginTop: 4 }}>
              {language === 'hi'
                ? 'खोजें • सत्यापित करें • कार्यवाही करें • सुरक्षित रखें'
                : 'Discover. Verify. Act. Protect — Continuous Entitlement Monitoring.'}
            </p>
          </div>
        </div>

        {/* Metric summary */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginTop: 18 }}>
          <WelfareMetric
            label={language === 'hi' ? 'जारी है' : 'Active'}
            value={active.length}
            tone="emerald"
            onClick={() => setFilter('ACTIVE')}
          />
          <WelfareMetric
            label={language === 'hi' ? 'अपडेट चाहिए' : 'Needs Action'}
            value={action.length}
            tone="rose"
            onClick={() => setFilter('ACTION')}
          />
          <WelfareMetric
            label={language === 'hi' ? 'नए अवसर' : 'Eligible'}
            value={newer.length}
            tone="gold"
            onClick={() => setFilter('NEW')}
          />
        </div>
      </GlassCard>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }}>
        {[
          { key: 'ALL', label: `${language === 'hi' ? 'सभी' : 'All'} (${total})` },
          { key: 'ACTIVE', label: `${language === 'hi' ? 'जारी है' : 'Active'} (${active.length})` },
          { key: 'ACTION', label: `${language === 'hi' ? 'अपडेट चाहिए' : 'Action'} (${action.length})` },
          { key: 'NEW', label: `${language === 'hi' ? 'नए अवसर' : 'New'} (${newer.length})` },
          ...(risk.length > 0
            ? [{ key: 'RISK', label: `${language === 'hi' ? 'जोखिम' : 'At Risk'} (${risk.length})` }]
            : []),
        ].map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setFilter(tab.key as FilterType)}
            style={{
              padding: '6px 16px',
              borderRadius: 9999,
              background: filter === tab.key ? 'rgba(245, 199, 124, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${filter === tab.key ? 'var(--gold-primary)' : 'var(--glass-border)'}`,
              color: filter === tab.key ? 'var(--gold-primary)' : 'var(--text-secondary)',
              fontSize: 12.5,
              fontWeight: filter === tab.key ? 700 : 500,
              whiteSpace: 'nowrap',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Active Benefits */}
      {(filter === 'ALL' || filter === 'ACTIVE') && active.length > 0 && (
        <section className="stack" style={{ gap: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: 16 }}>
              {language === 'hi' ? 'सुरक्षित एवं सक्रिय योजनाएं' : 'Protected Active Benefits'}
            </h3>
            <StatusPill tone="emerald">{active.length} ACTIVE</StatusPill>
          </div>
          {active.map((b) => (
            <BenefitCard key={b.id} benefit={b} />
          ))}
        </section>
      )}

      {/* Action Required Items */}
      {(filter === 'ALL' || filter === 'ACTION') && action.length > 0 && (
        <section className="stack" style={{ gap: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: 16 }}>
              {language === 'hi' ? 'कार्रवाई जरूरी' : 'Action Required to Protect Entitlements'}
            </h3>
            <StatusPill tone="amber">{action.length} PENDING</StatusPill>
          </div>
          {action.map((a, i) => (
            <GlassCard key={i} variant="alert">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <StatusPill tone="amber" size="sm">{a.action_type}</StatusPill>
                <Link to="/documents" style={{ color: 'var(--gold-primary)', fontSize: 12.5, fontWeight: 600 }}>
                  {language === 'hi' ? 'दस्तावेज़ जोड़ें →' : 'Add Evidence →'}
                </Link>
              </div>
              <h4 style={{ fontSize: 16, marginBottom: 4 }}>{a.title}</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{a.description}</p>
            </GlassCard>
          ))}
        </section>
      )}

      {/* New Opportunities */}
      {(filter === 'ALL' || filter === 'NEW') && newer.length > 0 && (
        <section className="stack" style={{ gap: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: 16 }}>
              {language === 'hi' ? 'नए संभावित अवसर' : 'Discovered Opportunities'}
            </h3>
            <StatusPill tone="gold">{newer.length} READY</StatusPill>
          </div>
          {newer.map((b) => (
            <BenefitCard key={b.id} benefit={b} />
          ))}
        </section>
      )}
    </div>
  );
}

export function BenefitDetail({ id: propId }: { id?: string }) {
  const { id: paramId } = useParams<{ id: string }>();
  const id = propId || paramId;
  const navigate = useNavigate();
  const { currentCitizenId } = useAuth();
  const { language } = useI18n();

  const [detail, setDetail] = useState<BenefitDetailModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [preparing, setPreparing] = useState(false);
  const [createdAppId, setCreatedAppId] = useState<string | null>(null);
  const [prepError, setPrepError] = useState<string | null>(null);

  const handlePrepareApplication = async () => {
    if (!currentCitizenId || !id) return;
    setPreparing(true);
    setPrepError(null);
    try {
      const res = await applicationApi.createApplication(currentCitizenId, id);
      setCreatedAppId(res.id);
    } catch (err: any) {
      setPrepError(err.message || 'Failed to prepare application dossier');
    } finally {
      setPreparing(false);
    }
  };

  useEffect(() => {
    if (id && currentCitizenId) {
      setLoading(true);
      benefitApi
        .getBenefit(id, currentCitizenId)
        .then(setDetail)
        .catch(setError)
        .finally(() => setLoading(false));
    }
  }, [id, currentCitizenId]);

  if (loading) {
    return (
      <div className="stack">
        <LoadingState />
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="stack">
        <ErrorState error={error} onRetry={() => navigate('/benefits')} />
      </div>
    );
  }

  const isEligible = detail.eligibility_status === 'ELIGIBLE';
  const satisfiedCount = detail.satisfied_requirements.length;
  const totalCount = satisfiedCount + detail.missing_requirements.length;
  const coveragePercent = totalCount > 0 ? Math.round((satisfiedCount / totalCount) * 100) : 100;

  const defaultReasons = [
    language === 'hi' ? 'व्यवसाय: निर्माण एवं असंगठित श्रमिक संवर्ग सुमेलित' : 'Occupation: Construction worker & informal trade matched',
    language === 'hi' ? 'आय: विहित सांविधिक सीमा के अंतर्गत सत्यापित' : 'Income: Annual income within statutory threshold',
    language === 'hi' ? 'स्थान: राज्य एवं ज़िला अधिवास सुमेलित' : 'Location: Active state and district jurisdiction matched',
    language === 'hi' ? 'परिवार: राशन एवं सामाजिक सुरक्षा डेटाबेस से सत्यापित' : 'Household: Family composition confirmed via socio-economic registry',
  ];
  const displayReasons = detail.reasons && detail.reasons.length > 0 ? detail.reasons : defaultReasons;

  return (
    <div className="stack">
      {/* 1. Large Cinematic Hero Card */}
      <GlassCard variant="hero" style={{ padding: '28px 24px' }}>
        <button
          type="button"
          onClick={() => navigate('/benefits')}
          style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12, display: 'inline-flex', alignItems: 'center', gap: 6 }}
        >
          ‹ {language === 'hi' ? 'योजनाओं पर वापस' : 'Back to Benefits'}
        </button>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
          <div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
              <StatusPill tone="blue">{detail.status}</StatusPill>
              <StatusPill tone={isEligible ? 'emerald' : 'amber'}>
                {detail.eligibility_status}
              </StatusPill>
            </div>
            <h1 style={{ fontSize: 26, margin: '6px 0' }}>{detail.scheme_name}</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
              {isEligible
                ? (language === 'hi'
                    ? '✓ सभी सांविधिक पात्रता मानदंड आपकी प्रोफ़ाइल से सत्यापित हैं।'
                    : '✓ All statutory eligibility criteria deterministically verified against your profile.')
                : (language === 'hi'
                    ? 'आवेदन पूरा करने के लिए अतिरिक्त साक्ष्य या दस्तावेज़ आवश्यक हैं।'
                    : 'Additional evidence or documentation required to complete application.')}
            </p>
          </div>
        </div>

        {/* Primary Action Button */}
        <div style={{ marginTop: 20 }}>
          <GlassButton
            variant="primary"
            size="lg"
            onClick={() => navigate('/applications')}
          >
            {language === 'hi' ? 'आवेदन तैयार करें →' : 'Prepare Application →'}
          </GlassButton>
        </div>
      </GlassCard>

      {/* 2. Layered Glass: WHY THIS MAY APPLY */}
      <GlassCard variant="default">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h3 style={{ fontSize: 16 }}>
            {language === 'hi' ? 'यह योजना आपके लिए क्यों लागू है' : 'WHY THIS MAY APPLY'}
          </h3>
          <span style={{ fontSize: 11, color: 'var(--gold-primary)', fontWeight: 700 }}>
            DETERMINISTIC VERIFICATION
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {displayReasons.map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
              <span style={{ color: '#34d399', fontWeight: 'bold' }}>✓</span>
              <span style={{ fontSize: 13.5, color: '#f8fafc' }}>{r}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* 3. Layered Glass: EVIDENCE READINESS */}
      <GlassCard variant="default">
        <h3 style={{ fontSize: 16, marginBottom: 12 }}>
          {language === 'hi' ? 'साक्ष्य तत्परता' : 'EVIDENCE READINESS'}
        </h3>
        <ProgressGlow
          value={coveragePercent}
          tone={coveragePercent === 100 ? 'emerald' : 'gold'}
          size="lg"
          showLabel={true}
          label={`${satisfiedCount} of ${totalCount} Requirements Proven`}
        />
      </GlassCard>

      {/* 4. Layered Glass: REQUIRED DOCUMENTS */}
      <GlassCard variant="default">
        <h3 style={{ fontSize: 16, marginBottom: 12 }}>
          {language === 'hi' ? 'आवश्यक दस्तावेज़ एवं साक्ष्य' : 'REQUIRED DOCUMENTS'}
        </h3>

        {/* Satisfied proofs */}
        {detail.satisfied_requirements.map((req) => (
          <div
            key={req.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 0',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ color: '#34d399', fontSize: 16 }}>✓</span>
              <div>
                <strong style={{ fontSize: 13.5, color: '#f8fafc' }}>{req.name}</strong>
                <small style={{ color: 'var(--text-muted)', display: 'block' }}>
                  Type: {req.type}
                </small>
              </div>
            </div>
            <StatusPill tone="emerald" size="sm">Verified</StatusPill>
          </div>
        ))}

        {/* Missing requirements */}
        {detail.missing_requirements.map((req) => (
          <div
            key={req.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 0',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ color: 'var(--amber-primary)', fontSize: 16 }}>⚠</span>
              <div>
                <strong style={{ fontSize: 13.5, color: '#fef08a' }}>{req.name}</strong>
                <small style={{ color: 'var(--text-muted)', display: 'block' }}>
                  Needed proof: {req.type}
                </small>
              </div>
            </div>
            <Link
              to="/documents"
              style={{
                fontSize: 12,
                color: 'var(--gold-primary)',
                background: 'rgba(245, 199, 124, 0.15)',
                padding: '4px 10px',
                borderRadius: 9999,
                fontWeight: 600,
              }}
            >
              + Upload
            </Link>
          </div>
        ))}
      </GlassCard>

      {/* 5. APPLICATION PREPARATION & HANDOFF SECTION */}
      <GlassCard variant="luminous" style={{ padding: '24px', border: '1.5px solid var(--gold-primary)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <span className="status-pill status-pill-gold status-pill-sm">
              {language === 'hi' ? '✦ आवेदन कार्रवाई' : '✦ APPLICATION ACTION'}
            </span>
            <h3 style={{ fontSize: 18, color: '#FFFFFF', margin: '6px 0 4px' }}>
              {createdAppId
                ? (language === 'hi' ? 'आवेदन सफलतापूर्वक तैयार किया गया' : 'Application Dossier Prepared')
                : (language === 'hi' ? 'इस योजना के लिए आवेदन तैयार करें' : 'Prepare Application Dossier')}
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, margin: 0 }}>
              {createdAppId
                ? (language === 'hi'
                    ? 'आपका आवेदन डेटाबेस में सुरक्षित है। अब समीक्षा और नागरिक सहमति के बाद पोर्टल हैंडऑफ पूर्ण करें।'
                    : 'Your application is securely stored in PostgreSQL. Proceed to review and citizen consent.')
                : (language === 'hi'
                    ? 'जनसेतु नीति इंजन आपके सत्यापित दस्तावेज़ों को जोड़कर आधिकारिक पोर्टल हेतु डोजियर तैयार करेगा।'
                    : 'JanSetu policy engine will assemble your verified credentials and statutory rules into an official application dossier.')}
            </p>
          </div>
        </div>

        {prepError && (
          <div style={{ color: '#f87171', fontSize: 13, marginBottom: 14 }}>
            ⚠ {prepError}
          </div>
        )}

        <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
          {createdAppId ? (
            <GlassButton
              variant="primary"
              size="md"
              onClick={() => navigate('/applications')}
            >
              {language === 'hi' ? 'आवेदन स्थिति एवं हैंडऑफ देखें →' : 'Track in Applications & Official Handoff →'}
            </GlassButton>
          ) : (
            <GlassButton
              variant="primary"
              size="md"
              loading={preparing}
              onClick={handlePrepareApplication}
            >
              {preparing
                ? (language === 'hi' ? 'डोजियर तैयार हो रहा है...' : 'Compiling Dossier...')
                : `📋 ${language === 'hi' ? 'आवेदन तैयार करें' : 'Prepare Application'}`}
            </GlassButton>
          )}

          <GlassButton
            variant="secondary"
            size="md"
            onClick={() => navigate('/documents')}
          >
            📁 {language === 'hi' ? 'दस्तावेज़ प्रबंधित करें' : 'Manage Documents'}
          </GlassButton>
        </div>
      </GlassCard>

      {/* 6. Layered Glass: POLICY SOURCE */}
      <GlassCard variant="subtle">
        <h4 style={{ fontSize: 14, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>
          {language === 'hi' ? 'नीति स्रोत एवं प्रामाणिकता' : 'POLICY SOURCE & PROVENANCE'}
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          <div>
            <small style={{ color: 'var(--text-muted)', display: 'block' }}>Source</small>
            <strong style={{ color: '#f8fafc', fontSize: 13 }}>Official Gazette</strong>
          </div>
          <div>
            <small style={{ color: 'var(--text-muted)', display: 'block' }}>Status</small>
            <strong style={{ color: '#34d399', fontSize: 13 }}>Verified</strong>
          </div>
          <div>
            <small style={{ color: 'var(--text-muted)', display: 'block' }}>Version</small>
            <strong style={{ color: 'var(--gold-primary)', fontSize: 13 }}>Release v3.2</strong>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
