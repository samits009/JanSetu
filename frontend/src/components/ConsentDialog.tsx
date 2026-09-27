import React from 'react';
import { ConsentRequestData } from '../domain/models';
import { useI18n } from '../i18n/I18nContext';
import { GlassCard, GlassButton, StatusPill } from './common';

interface ConsentDialogProps {
  consentRequest: ConsentRequestData;
  applicantName?: string;
  schemeName?: string;
  onGrant: () => void;
  onDeny: () => void;
}

export function ConsentDialog({
  consentRequest,
  applicantName = 'Citizen Applicant',
  schemeName = 'BOCW Welfare Assistance',
  onGrant,
  onDeny,
}: ConsentDialogProps) {
  const { language } = useI18n();

  return (
    <GlassCard
      variant="luminous"
      style={{
        border: '1.5px solid var(--gold-primary)',
        boxShadow: '0 0 35px rgba(245, 199, 124, 0.25)',
        padding: '24px 22px',
        margin: '20px 0',
      }}
      role="alertdialog"
      aria-labelledby="consent-title"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <StatusPill tone="gold" pulse={true}>
          {language === 'hi' ? 'संप्रभु नागरिक सहमति' : 'SOVEREIGN CITIZEN CONSENT'}
        </StatusPill>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          {language === 'hi' ? 'स्पष्ट हैंडऑफ प्राधिकरण' : 'Explicit Handoff Authorization'}
        </span>
      </div>

      <h2 id="consent-title" style={{ fontSize: 22, marginBottom: 8, color: '#FFFFFF' }}>
        {language === 'hi' ? 'क्या आप आगे बढ़ने के लिए तैयार हैं?' : 'Ready to continue?'}
      </h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, marginBottom: 18 }}>
        {language === 'hi'
          ? 'सरकारी पोर्टल पर संकलित साक्ष्य प्रेषित करने से पूर्व जनसेतु को आपके स्पष्ट प्राधिकरण की आवश्यकता है।'
          : 'JanSetu requires your explicit authorization before transmitting compiled evidence to the government portal.'}
      </p>

      {/* Details Box */}
      <div
        style={{
          background: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 16,
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
          marginBottom: 18,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            {language === 'hi' ? 'योजना' : 'Scheme'}
          </span>
          <strong style={{ color: '#f8fafc', fontSize: 13 }}>{schemeName}</strong>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            {language === 'hi' ? 'आवेदक' : 'Applicant'}
          </span>
          <strong style={{ color: '#f8fafc', fontSize: 13 }}>{applicantName}</strong>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            {language === 'hi' ? 'कार्रवाई' : 'Action'}
          </span>
          <strong style={{ color: 'var(--gold-primary)', fontSize: 13 }}>
            {consentRequest.action || (language === 'hi' ? 'आधिकारिक पोर्टल हैंडऑफ एवं डोजियर दाखिला' : 'Official Portal Handoff & Dossier Filing')}
          </strong>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            {language === 'hi' ? 'गंतव्य' : 'Destination'}
          </span>
          <strong style={{ color: '#7dd3fc', fontSize: 13 }}>
            {consentRequest.destination || (language === 'hi' ? 'सरकारी प्रत्यक्ष लाभ पोर्टल (DPI)' : 'Government Direct Benefits Portal (DPI)')}
          </strong>
        </div>

        {consentRequest.data_accessed && consentRequest.data_accessed.length > 0 && (
          <div>
            <span style={{ color: 'var(--text-muted)', fontSize: 13, display: 'block', marginBottom: 6 }}>
              {language === 'hi' ? 'हस्तांतरित दस्तावेज़ एवं साक्ष्य:' : 'Documents & Evidence Transmitted:'}
            </span>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {consentRequest.data_accessed.map((doc, idx) => (
                <span
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.08)',
                    border: '1px solid var(--glass-border)',
                    padding: '3px 10px',
                    borderRadius: 9999,
                    fontSize: 12,
                    color: '#e2e8f0',
                  }}
                >
                  ✓ {doc}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Sovereign Trust Assurance */}
      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <p style={{ color: 'var(--gold-primary)', fontWeight: 700, fontSize: 15, margin: 0 }}>
          {language === 'hi' ? 'नियंत्रण आपके हाथ में है।' : 'You are in control.'}
        </p>
        <small style={{ color: 'var(--text-muted)', fontSize: 12 }}>
          {language === 'hi'
            ? 'जनसेतु आपकी स्पष्ट सहमति के बिना कभी भी कोई डेटा साझा नहीं करता है।'
            : 'JanSetu never shares your data without verifiable cryptographic consent.'}
        </small>
      </div>

      {/* Explicit Actions */}
      <div style={{ display: 'flex', gap: 12 }}>
        <GlassButton variant="primary" size="md" onClick={onGrant}>
          {language === 'hi' ? 'सहमति दें और आगे बढ़ें →' : 'Give Consent & Continue →'}
        </GlassButton>
        <GlassButton variant="secondary" size="md" onClick={onDeny}>
          {language === 'hi' ? 'पुनः समीक्षा करें' : 'Review Again'}
        </GlassButton>
      </div>
    </GlassCard>
  );
}
