import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import { citizenApi } from '../services/citizenApi';
import { CitizenProfile } from '../domain/models';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import {
  GlassCard,
  GlassButton,
  StatusPill,
} from '../components/common';

export function Profile() {
  const { user, currentCitizenId, logout } = useAuth();
  const { language, setLanguage, syncError, clearSyncError, isSyncing, t } = useI18n();
  const navigate = useNavigate();

  const [citizen, setCitizen] = useState<CitizenProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (currentCitizenId) {
      setLoading(true);
      citizenApi
        .getCitizen(currentCitizenId)
        .then(setCitizen)
        .catch(setError)
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [currentCitizenId]);

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  if (loading) {
    return (
      <div className="stack">
        <LoadingState />
      </div>
    );
  }

  if (error) {
    return (
      <div className="stack">
        <ErrorState error={error} />
      </div>
    );
  }

  const currentLocation = citizen?.locations?.find((l) => l.is_active)?.district || 'Delhi';
  const currentState = citizen?.locations?.find((l) => l.is_active)?.state || 'Delhi';
  const occupation = citizen?.employments?.find((e) => e.is_active)?.occupation || 'Construction Worker';
  const citizenName = user?.name || citizen?.name || user?.email?.split('@')[0] || 'Citizen';
  const initials = citizenName.trim().slice(0, 2).toUpperCase();

  return (
    <div className="stack">
      {/* 1. Sovereign Citizen Identity Hero Card */}
      <GlassCard variant="hero" style={{ padding: '28px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--gold-primary), #b45309)',
              color: '#ffffff',
              display: 'grid',
              placeItems: 'center',
              fontSize: 24,
              fontWeight: 800,
              boxShadow: '0 0 25px rgba(245, 199, 124, 0.4)',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              flexShrink: 0,
            }}
          >
            {initials}
          </div>

          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
              <StatusPill tone="emerald" size="sm">
                {language === 'hi' ? 'सत्यापित पहचान' : 'Verified Identity'}
              </StatusPill>
              <StatusPill tone="blue" size="sm">
                {language === 'hi' ? 'आधार से लिंक' : 'Aadhaar Linked'}
              </StatusPill>
            </div>
            <h1 style={{ fontSize: 22, color: 'var(--text-primary)', margin: 0 }}>
              {citizenName}
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, margin: '4px 0 0' }}>
              {occupation} · {currentLocation}, {currentState}
            </p>
          </div>

          <GlassButton
            variant="secondary"
            size="sm"
            fullWidth={false}
            onClick={() => navigate('/onboarding')}
          >
            ✏️ {language === 'hi' ? 'संपादित करें' : 'Edit'}
          </GlassButton>
        </div>
      </GlassCard>

      {/* 2. Bilingual Preference Card */}
      <GlassCard variant="default">
        <h3 style={{ fontSize: 16, marginBottom: 4 }}>
          🌐 {language === 'hi' ? 'पसंदीदा भाषा' : 'Preferred Language'}
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
          {language === 'hi'
            ? 'अपनी पसंदीदा भाषा चुनें। सभी योजनाएं, नियम, पात्रता विवरण और AI सहायक इसी भाषा में तुरंत अनुकूलित होंगे।'
            : 'Select your preferred interface language. All scheme evaluations, reasons, and AI interactions will adapt instantly.'}
        </p>

        <div style={{ display: 'flex', gap: 12 }}>
          <button
            type="button"
            onClick={() => setLanguage('hi')}
            style={{
              flex: 1,
              padding: '12px 18px',
              borderRadius: 9999,
              background: language === 'hi' ? 'rgba(245, 199, 124, 0.22)' : 'rgba(255, 255, 255, 0.05)',
              border: `1.5px solid ${language === 'hi' ? 'var(--gold-primary)' : 'var(--glass-border)'}`,
              color: language === 'hi' ? 'var(--gold-primary)' : 'var(--text-secondary)',
              fontSize: 14,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: language === 'hi' ? '0 0 16px rgba(245, 199, 124, 0.3)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
          >
            <span>🇮🇳</span> हिंदी (Hindi)
          </button>

          <button
            type="button"
            onClick={() => setLanguage('en')}
            style={{
              flex: 1,
              padding: '12px 18px',
              borderRadius: 9999,
              background: language === 'en' ? 'rgba(245, 199, 124, 0.22)' : 'rgba(255, 255, 255, 0.05)',
              border: `1.5px solid ${language === 'en' ? 'var(--gold-primary)' : 'var(--glass-border)'}`,
              color: language === 'en' ? 'var(--gold-primary)' : 'var(--text-secondary)',
              fontSize: 14,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: language === 'en' ? '0 0 16px rgba(245, 199, 124, 0.3)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
          >
            <span>🇬🇧</span> English
          </button>
        </div>

        {syncError && (
          <div
            style={{
              marginTop: 14,
              padding: '10px 14px',
              borderRadius: 8,
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              color: '#fca5a5',
              fontSize: 13,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 8,
            }}
          >
            <span>⚠️ {syncError}</span>
            <button
              type="button"
              onClick={() => setLanguage(language)}
              style={{
                background: 'rgba(239, 68, 68, 0.3)',
                border: 'none',
                color: '#fff',
                padding: '4px 10px',
                borderRadius: 4,
                cursor: 'pointer',
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              {language === 'hi' ? 'पुनः प्रयास करें' : 'Retry'}
            </button>
          </div>
        )}

        {isSyncing && (
          <p style={{ color: 'var(--text-secondary)', fontSize: 12, marginTop: 8, marginBottom: 0 }}>
            ⏳ {language === 'hi' ? 'सर्वर पर प्राथमिकता सुरक्षित की जा रही है...' : 'Saving preference to database...'}
          </p>
        )}
      </GlassCard>

      {/* 3. Sovereign Trust & Privacy Charter */}
      <GlassCard variant="default">
        <h3 style={{ fontSize: 16, marginBottom: 12 }}>
          🛡️ {language === 'hi' ? 'नागरिक संप्रभुता एवं सुरक्षा चार्टर' : 'Sovereign Citizen Trust Charter'}
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            {
              hi: 'कठोर पात्रता केवल आधिकारिक नियमों से तय होती है (LLM कभी निर्णय नहीं लेता)',
              en: 'Deterministic policy evaluation only (LLM is never the eligibility authority)',
            },
            {
              hi: 'सत्यापित दस्तावेज़ों से स्वतः सटीक आवेदन प्रारूप तैयार होता है',
              en: 'Applications are compiled strictly from verified cryptographic evidence',
            },
            {
              hi: 'किसी भी सरकारी पोर्टल में जाने से पहले नागरिक की स्पष्ट सहमति आवश्यक है',
              en: 'Every external handoff requires explicit sovereign citizen consent',
            },
            {
              hi: 'डेटाबेस में पूर्ण ऑडिट ट्रेल सुरक्षित रहता है',
              en: 'Complete audit trail persisted to PostgreSQL',
            },
          ].map((item, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ color: '#34d399', fontWeight: 'bold' }}>✓</span>
              <span style={{ fontSize: 13, color: 'var(--text-primary)' }}>
                {language === 'hi' ? item.hi : item.en}
              </span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* 4. Session & Security */}
      <GlassCard variant="alert" style={{ borderColor: 'rgba(244, 63, 94, 0.3)' }}>
        <h3 style={{ fontSize: 16, color: '#fca5a5', marginBottom: 4 }}>
          {language === 'hi' ? 'खाता सुरक्षा' : 'Account Security'}
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
          {user?.email} · {language === 'hi' ? 'सक्रिय सत्र' : 'Active Session'}
        </p>

        <GlassButton
          variant="danger"
          size="md"
          fullWidth={false}
          onClick={handleLogout}
          style={{
            background: 'rgba(244, 63, 94, 0.15)',
            border: '1px solid rgba(244, 63, 94, 0.4)',
            color: '#f87171',
          }}
        >
          ⎋ {t('profile.logoutBtn', 'Log Out of JanSetu')}
        </GlassButton>
      </GlassCard>
    </div>
  );
}
