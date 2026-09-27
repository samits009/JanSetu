import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BenefitCard } from '../components/BenefitCard';
import { useAuth } from '../auth/AuthContext';
import { useApi } from '../hooks/useApi';
import { useI18n } from '../i18n/I18nContext';
import { welfareApi } from '../services/welfareApi';
import { SurvivalResult } from '../domain/models';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import {
  GlassCard,
  GlassButton,
  GlassSelect,
  StatusPill,
  WelfareMetric,
} from '../components/common';
import {
  STATES_LIST,
  UTS_LIST,
  getDistrictsForState,
} from '../data/indiaLocations';

export function SurvivalMap() {
  const { currentCitizenId } = useAuth();
  const { language } = useI18n();
  const navigate = useNavigate();
  const [targetState, setTargetState] = useState('Delhi');
  const [targetDistrict, setTargetDistrict] = useState('Central Delhi');

  const { data: survivalData, loading, error, execute } = useApi<SurvivalResult, [string, any]>(
    welfareApi.simulateLocationChange,
    false
  );

  const stateGroups = useMemo(
    () => [
      {
        label: language === 'hi' ? '🏛️ राज्य (States)' : '🏛️ States of India',
        options: STATES_LIST.map((s) => ({ label: s, value: s })),
      },
      {
        label: language === 'hi' ? '🇮🇳 केंद्र शासित प्रदेश (Union Territories)' : '🇮🇳 Union Territories',
        options: UTS_LIST.map((u) => ({ label: u, value: u })),
      },
    ],
    [language]
  );

  const availableDistricts = useMemo(() => getDistrictsForState(targetState), [targetState]);

  const handleStateChange = (newState: string) => {
    setTargetState(newState);
    const districts = getDistrictsForState(newState);
    if (!districts.includes(targetDistrict)) {
      setTargetDistrict(districts[0] || '');
    }
  };

  const handleSimulate = () => {
    execute(currentCitizenId, { state: targetState, district: targetDistrict });
  };

  return (
    <div className="stack">
      {/* 1. Hero Overview */}
      <GlassCard variant="hero">
        <span className="status-pill status-pill-sky status-pill-sm" style={{ marginBottom: 6 }}>
          ✦ INTERSTATE WELFARE CONTINUITY & SURVIVAL MAP
        </span>
        <h1 style={{ fontSize: 24 }}>
          {language === 'hi' ? 'स्थान परिवर्तन एवं उत्तरजीविता मानचित्र' : 'Interstate Benefit Survival Map'}
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, margin: '4px 0 16px' }}>
          {language === 'hi'
            ? 'जब नागरिक एक राज्य से दूसरे राज्य में जाते हैं, तो जनसेतु राशन, स्वास्थ्य और निर्माण श्रमिक पेंशन की पोर्टेबिलिटी की पूर्व-गणना करता है।'
            : 'Simulate migration to safeguard your food security, medical, and cash welfare benefits across state borders.'}
        </p>
      </GlassCard>

      {/* 2. Simulation Capsule Card */}
      <GlassCard variant="default">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h3 style={{ fontSize: 17 }}>
            {language === 'hi' ? 'स्थानांतरण सिमुलेशन' : 'Migration Portability Simulation'}
          </h3>
          <StatusPill tone="blue">PREDICTIVE</StatusPill>
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
          {language === 'hi'
            ? 'गंतव्य राज्य और ज़िला चुनें ताकि जनसेतु लागू योजनाओं की उत्तरजीविता दर की गणना कर सके।'
            : 'Select target destination to calculate statutory benefit portability and pre-empt entitlement loss.'}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 18 }}>
          <GlassSelect
            label={language === 'hi' ? 'गंतव्य राज्य / केंद्र शासित प्रदेश' : 'Destination State / UT'}
            placeholder={language === 'hi' ? '-- राज्य / केंद्र शासित प्रदेश चुनें --' : '-- Select State / UT --'}
            groups={stateGroups}
            value={targetState}
            onChange={(e) => handleStateChange(e.target.value)}
          />

          <GlassSelect
            label={language === 'hi' ? 'गंतव्य ज़िला' : 'Destination District'}
            placeholder={
              targetState
                ? (language === 'hi' ? '-- ज़िला चुनें --' : '-- Select District --')
                : (language === 'hi' ? '-- पहले राज्य चुनें --' : '-- Select State First --')
            }
            disabled={!targetState || availableDistricts.length === 0}
            options={availableDistricts.map((d) => ({ label: d, value: d }))}
            value={targetDistrict}
            onChange={(e) => setTargetDistrict(e.target.value)}
          />
        </div>

        <GlassButton
          type="button"
          variant="primary"
          size="lg"
          loading={loading}
          onClick={handleSimulate}
        >
          {loading
            ? (language === 'hi' ? 'सिमुलेशन जारी है...' : 'Simulating Impact...')
            : (language === 'hi' ? 'कल्याण प्रभाव की जांच करें →' : 'Simulate Migration Impact →')}
        </GlassButton>
      </GlassCard>

      {error && <ErrorState error={error} onRetry={handleSimulate} />}
      {loading && <LoadingState />}

      {/* 3. Results Section */}
      {survivalData && !loading && (
        <section className="stack" style={{ gap: 14 }}>
          {/* Metric Grid */}
          <div className="welfare-metrics-grid">
            <WelfareMetric
              label={language === 'hi' ? 'जारी रहेगा' : 'Continued'}
              value={survivalData.continued_benefits.length}
              subValue="Ported"
              tone="emerald"
            />
            <WelfareMetric
              label={language === 'hi' ? 'जोखिम में' : 'At Risk'}
              value={survivalData.at_risk_benefits.length}
              subValue="Needs Renewal"
              tone="rose"
            />
            <WelfareMetric
              label={language === 'hi' ? 'नया अवसर' : 'New Schemes'}
              value={survivalData.new_benefits.length}
              subValue={`In ${targetState}`}
              tone="blue"
            />
          </div>

          {/* Action Required Banner */}
          {survivalData.required_actions.length > 0 && (
            <GlassCard variant="alert">
              <strong style={{ display: 'block', fontSize: 14.5, color: '#fef08a', marginBottom: 8 }}>
                ⚠️ {language === 'hi' ? 'कल्याण निरंतरता के लिए आवश्यक कदम' : 'Actions Required to Protect Benefits'}
              </strong>
              <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-secondary)', fontSize: 13, display: 'flex', flexDirection: 'column', gap: 6 }}>
                {survivalData.required_actions.map((a, i) => (
                  <li key={i}>
                    <strong style={{ color: '#f8fafc' }}>{a.title}:</strong> {a.description}
                  </li>
                ))}
              </ul>
            </GlassCard>
          )}

          {/* Continued Benefits */}
          {survivalData.continued_benefits.length > 0 && (
            <div className="stack" style={{ gap: 10 }}>
              <h3 style={{ fontSize: 16 }}>
                ✓ {language === 'hi' ? 'निर्बाध रूप से जारी रहने वाले लाभ' : 'Continued Uninterrupted Benefits'}
              </h3>
              {survivalData.continued_benefits.map((b) => (
                <BenefitCard key={b.id} benefit={b} />
              ))}
            </div>
          )}

          {/* At Risk Benefits */}
          {survivalData.at_risk_benefits.length > 0 && (
            <div className="stack" style={{ gap: 10 }}>
              <h3 style={{ fontSize: 16, color: '#fb7185' }}>
                ⚠ {language === 'hi' ? 'जोखिम में लाभ' : 'Benefits At Risk in New State'}
              </h3>
              {survivalData.at_risk_benefits.map((b) => (
                <BenefitCard key={b.id} benefit={b} />
              ))}
            </div>
          )}

          {/* New Opportunities */}
          {survivalData.new_benefits.length > 0 && (
            <div className="stack" style={{ gap: 10 }}>
              <h3 style={{ fontSize: 16, color: 'var(--gold-primary)' }}>
                ✦ {language === 'hi' ? `${targetState} में नए अवसर` : `New Welfare Schemes in ${targetState}`}
              </h3>
              {survivalData.new_benefits.map((b) => (
                <BenefitCard key={b.id} benefit={b} />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
