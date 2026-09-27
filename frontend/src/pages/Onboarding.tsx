import React, { useMemo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import { apiClient } from '../services/apiClient';
import {
  GlassCard,
  GlassButton,
  GlassInput,
  GlassSelect,
  StatusPill,
} from '../components/common';
import {
  STATES_LIST,
  UTS_LIST,
  getDistrictsForState,
} from '../data/indiaLocations';

export function Onboarding() {
  const { user, refreshUser } = useAuth();
  const { t, language } = useI18n();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [name, setName] = useState(user?.name || '');
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState('male');
  const [phone, setPhone] = useState(user?.phone || '');

  const [currentState, setCurrentState] = useState('');
  const [currentDistrict, setCurrentDistrict] = useState('');
  const [permanentState, setPermanentState] = useState('');
  const [permanentDistrict, setPermanentDistrict] = useState('');
  const [sameAsCurrent, setSameAsCurrent] = useState(false);

  const [employmentStatus, setEmploymentStatus] = useState('informal_labor');
  const [occupation, setOccupation] = useState('');
  const [annualIncome, setAnnualIncome] = useState('');
  const [employerType, setEmployerType] = useState('');

  const [householdMembers, setHouseholdMembers] = useState('1');
  const [dependents, setDependents] = useState('0');

  // Bifurcated Location Helpers
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

  const currentDistricts = useMemo(() => getDistrictsForState(currentState), [currentState]);
  const permanentDistricts = useMemo(() => getDistrictsForState(permanentState), [permanentState]);

  const handleCurrentStateChange = (selectedState: string) => {
    setCurrentState(selectedState);
    const districts = selectedState ? getDistrictsForState(selectedState) : [];
    const newDistrict = districts.includes(currentDistrict) ? currentDistrict : (districts[0] || '');
    setCurrentDistrict(newDistrict);

    if (sameAsCurrent) {
      setPermanentState(selectedState);
      setPermanentDistrict(newDistrict);
    }
  };

  const handleCurrentDistrictChange = (selectedDistrict: string) => {
    setCurrentDistrict(selectedDistrict);
    if (sameAsCurrent) {
      setPermanentDistrict(selectedDistrict);
    }
  };

  const handlePermanentStateChange = (selectedState: string) => {
    setPermanentState(selectedState);
    const districts = getDistrictsForState(selectedState);
    if (!districts.includes(permanentDistrict)) {
      setPermanentDistrict(districts[0] || '');
    }
  };

  const handleSameAsCurrentToggle = (checked: boolean) => {
    setSameAsCurrent(checked);
    if (checked) {
      setPermanentState(currentState);
      setPermanentDistrict(currentDistrict);
    }
  };

  useEffect(() => {
    // Check if citizen profile already has saved progress in PostgreSQL to resume
    apiClient
      .get<{ profile: any }>('/api/citizens/me')
      .then((res) => {
        const p = res?.profile;
        if (!p) return;
        if (p.name) setName(p.name);
        if (p.dob) setDob(p.dob);
        if (p.gender) setGender(p.gender);
        if (p.phone) setPhone(p.phone);

        const currentLoc = p.locations?.find((l: any) => l.location_type === 'CURRENT' && l.is_active);
        if (currentLoc) {
          setCurrentState(currentLoc.state || '');
          setCurrentDistrict(currentLoc.district || '');
        }

        const permLoc = p.locations?.find((l: any) => l.location_type === 'HOME' && l.is_active);
        if (permLoc) {
          setPermanentState(permLoc.state || '');
          setPermanentDistrict(permLoc.district || '');
        }

        const emp = p.employments?.find((e: any) => e.is_active);
        if (emp) {
          if (emp.occupation) setOccupation(emp.occupation);
          if (emp.employment_status) setEmploymentStatus(emp.employment_status);
          if (emp.annual_income != null) setAnnualIncome(String(emp.annual_income));
          if (emp.employer_name) setEmployerType(emp.employer_name);
        }

        if (p.onboarding_step && p.onboarding_step >= 1 && p.onboarding_step <= 4) {
          setStep(p.onboarding_step);
        }
      })
      .catch(() => {});
  }, []);

  const handleNext = async () => {
    setError(null);
    if (step === 1 && !name.trim()) {
      setError(t('auth.errorRequired', 'Please enter your full name'));
      return;
    }
    if (step === 2 && (!currentState.trim() || !currentDistrict.trim())) {
      setError(t('auth.errorRequired', 'Please enter state and district'));
      return;
    }

    const nextStep = step + 1;
    setIsSubmitting(true);
    try {
      await apiClient.put('/api/citizens/me/onboarding/step', {
        step: nextStep,
        name,
        date_of_birth: dob || undefined,
        gender,
        phone,
        current_state: currentState || undefined,
        current_district: currentDistrict || undefined,
        permanent_state: permanentState || undefined,
        permanent_district: permanentDistrict || undefined,
        employment_status: employmentStatus || undefined,
        occupation: occupation || undefined,
        annual_income: annualIncome ? parseFloat(annualIncome) : undefined,
        employer_name: employerType || undefined,
        household_members: parseInt(householdMembers, 10) || 1,
        dependents: parseInt(dependents, 10) || 0,
      });
      setStep(nextStep);
    } catch (err: any) {
      setError(err?.message || 'Failed to save step progress to server');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBack = () => {
    setError(null);
    if (step > 1) {
      const prevStep = step - 1;
      setStep(prevStep);
      apiClient.put('/api/citizens/me/onboarding/step', { step: prevStep }).catch(() => {});
    }
  };

  const handleComplete = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await apiClient.post('/api/citizens/me/onboarding', {
        name,
        date_of_birth: dob,
        gender,
        phone,
        current_state: currentState,
        current_district: currentDistrict,
        permanent_state: permanentState,
        permanent_district: permanentDistrict,
        employment_status: employmentStatus,
        occupation,
        annual_income: parseFloat(annualIncome) || 0,
        employer_name: employerType || undefined,
        household_members: parseInt(householdMembers, 10) || 1,
        dependents: parseInt(dependents, 10) || 0,
      });

      await refreshUser();
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err?.message || 'Failed to persist citizen profile to PostgreSQL.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const steps = [
    { num: 1, label: t('onboarding.step1', 'Personal') },
    { num: 2, label: t('onboarding.step2', 'Location') },
    { num: 3, label: t('onboarding.step3', 'Employment') },
    { num: 4, label: t('onboarding.step4', 'Household') },
  ];

  return (
    <div className="stack" style={{ maxWidth: 600, margin: '0 auto' }}>
      {/* Header */}
      <GlassCard variant="hero" style={{ textAlign: 'center', padding: '24px 20px' }}>
        <StatusPill tone="gold" size="sm">
          {t('onboarding.badge', 'Citizen Profile Setup')}
        </StatusPill>
        <h1 style={{ fontSize: 24, margin: '10px 0 6px', color: '#ffffff' }}>
          {t('onboarding.title', 'Build Your Welfare Identity')}
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.5, margin: 0 }}>
          {t(
            'onboarding.subtitle',
            'Provide your household and occupation details once. JanSetu continuously matches you with entitled welfare schemes.'
          )}
        </p>

        {/* 4-Step Capsule Stepper */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 22, padding: '0 8px' }}>
          {steps.map((s) => {
            const isPassed = step > s.num;
            const isCurrent = step === s.num;

            return (
              <div
                key={s.num}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 6,
                  flex: 1,
                }}
              >
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    background: isPassed
                      ? 'rgba(16, 185, 129, 0.25)'
                      : isCurrent
                      ? 'rgba(245, 199, 124, 0.25)'
                      : 'rgba(255, 255, 255, 0.06)',
                    border: `1.5px solid ${
                      isPassed ? '#10b981' : isCurrent ? 'var(--gold-primary)' : 'var(--glass-border)'
                    }`,
                    color: isPassed ? '#34d399' : isCurrent ? 'var(--gold-primary)' : 'var(--text-muted)',
                    display: 'grid',
                    placeItems: 'center',
                    fontSize: 12,
                    fontWeight: 700,
                    boxShadow: isCurrent ? '0 0 14px rgba(245, 199, 124, 0.4)' : 'none',
                  }}
                >
                  {isPassed ? '✓' : s.num}
                </div>
                <span
                  style={{
                    fontSize: 11,
                    color: isCurrent ? 'var(--gold-primary)' : 'var(--text-muted)',
                    fontWeight: isCurrent ? 700 : 500,
                  }}
                >
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>
      </GlassCard>

      {error && (
        <div className="glass-input-error" role="alert" style={{ fontSize: 13 }}>
          <span>⚠</span>
          <span>{error}</span>
        </div>
      )}

      {/* Main Form Body */}
      <GlassCard variant="default">
        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h2 style={{ fontSize: 17, color: 'var(--gold-primary)', margin: 0 }}>
              1. {t('onboarding.step1', 'Personal Details')}
            </h2>

            <GlassInput
              label={`${t('onboarding.fullName', 'Full Legal Name')} *`}
              placeholder={t('onboarding.fullNamePlaceholder', 'As shown on Aadhaar')}
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <GlassInput
                type="date"
                label={`${t('onboarding.dob', 'Date of Birth')} *`}
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                required
              />

              <GlassSelect
                label={`${t('onboarding.gender', 'Gender')} *`}
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                options={[
                  { label: t('onboarding.genderMale', 'Male'), value: 'male' },
                  { label: t('onboarding.genderFemale', 'Female'), value: 'female' },
                  { label: t('onboarding.genderOther', 'Other'), value: 'other' },
                ]}
                required
              />
            </div>

            <GlassInput
              type="tel"
              label={t('auth.phoneLabel', 'Mobile Number')}
              placeholder="9876543210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>
        )}

        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <h2 style={{ fontSize: 17, color: 'var(--gold-primary)', margin: '0 0 4px' }}>
                2. {t('onboarding.step2', 'Location & Residence')}
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: 13, margin: 0 }}>
                {language === 'hi'
                  ? 'अपना वर्तमान और स्थायी निवास चुनें। सभी ज़िले संबंधित राज्य/केंद्र शासित प्रदेश के अनुसार व्यवस्थित हैं।'
                  : 'Select your residing and domicile jurisdiction. All districts are dynamically bifurcated by State and UT.'}
              </p>
            </div>

            {/* Current Residing Location */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <GlassSelect
                label={`${t('onboarding.currentState', 'Current Residing State')} *`}
                placeholder={language === 'hi' ? '-- राज्य / केंद्र शासित प्रदेश चुनें --' : '-- Select State / UT --'}
                groups={stateGroups}
                value={currentState}
                onChange={(e) => handleCurrentStateChange(e.target.value)}
                required
              />

              <GlassSelect
                label={`${t('onboarding.currentDistrict', 'Current District')} *`}
                placeholder={
                  currentState
                    ? (language === 'hi' ? '-- ज़िला चुनें --' : '-- Select District --')
                    : (language === 'hi' ? '-- पहले राज्य चुनें --' : '-- Select State First --')
                }
                disabled={!currentState || currentDistricts.length === 0}
                options={currentDistricts.map((d) => ({ label: d, value: d }))}
                value={currentDistrict}
                onChange={(e) => handleCurrentDistrictChange(e.target.value)}
                required
              />
            </div>

            {/* Quick Sync Toggle */}
            <label
              className="auth-checkbox-label"
              style={{
                fontSize: 12.5,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                margin: '-4px 0 2px',
              }}
            >
              <input
                type="checkbox"
                checked={sameAsCurrent}
                onChange={(e) => handleSameAsCurrentToggle(e.target.checked)}
              />
              <span>
                {language === 'hi'
                  ? 'स्थायी पता वर्तमान निवास के समान है (Permanent location same as current)'
                  : 'Permanent / Domicile location is the same as current residence'}
              </span>
            </label>

            {/* Permanent / Domicile Location */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <GlassSelect
                label={t('onboarding.permanentState', 'Permanent / Domicile State')}
                placeholder={language === 'hi' ? '-- राज्य / केंद्र शासित प्रदेश चुनें --' : '-- Select State / UT --'}
                groups={stateGroups}
                disabled={sameAsCurrent}
                value={permanentState}
                onChange={(e) => handlePermanentStateChange(e.target.value)}
              />

              <GlassSelect
                label={t('onboarding.permanentDistrict', 'Permanent District')}
                placeholder={
                  permanentState
                    ? (language === 'hi' ? '-- ज़िला चुनें --' : '-- Select District --')
                    : (language === 'hi' ? '-- पहले राज्य चुनें --' : '-- Select State First --')
                }
                disabled={sameAsCurrent || !permanentState || permanentDistricts.length === 0}
                options={permanentDistricts.map((d) => ({ label: d, value: d }))}
                value={permanentDistrict}
                onChange={(e) => setPermanentDistrict(e.target.value)}
              />
            </div>

            {/* Informational Guidance Capsule */}
            <div
              style={{
                background: 'rgba(245, 199, 124, 0.08)',
                border: '1px solid rgba(245, 199, 124, 0.22)',
                borderRadius: 14,
                padding: '12px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
              }}
            >
              <span style={{ color: 'var(--gold-primary)', fontSize: 16 }}>📍</span>
              <p style={{ margin: 0, fontSize: 12.5, color: '#e2e8f0', lineHeight: 1.45 }}>
                {language === 'hi'
                  ? 'राज्य एवं ज़िला चयन आपके राशन पोर्टेबिलिटी, भवन निर्माण श्रमिक बोर्ड (BOCW) और राज्य कल्याणकारी योजनाओं को स्वतः निर्धारित करता है।'
                  : 'State and district selections automatically determine jurisdiction-specific entitlements, BOCW welfare board rights, and interstate portability.'}
              </p>
            </div>
          </div>
        )}

        {step === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h2 style={{ fontSize: 17, color: 'var(--gold-primary)', margin: 0 }}>
              3. {t('onboarding.step3', 'Employment & Livelihood')}
            </h2>

            <GlassSelect
              label={`${t('onboarding.employmentStatus', 'Employment Status')} *`}
              value={employmentStatus}
              onChange={(e) => setEmploymentStatus(e.target.value)}
              options={[
                { label: t('onboarding.statusInformal', 'Informal / Construction Worker (BOCW)'), value: 'informal_labor' },
                { label: t('onboarding.statusSalaried', 'Salaried / Formal'), value: 'salaried' },
                { label: t('onboarding.statusSelfEmployed', 'Self-Employed / Vendor'), value: 'self_employed' },
                { label: t('onboarding.statusAgricultural', 'Farmer / Agricultural Worker'), value: 'agricultural' },
                { label: t('onboarding.statusUnemployed', 'Unemployed / Seeking Work'), value: 'unemployed' },
              ]}
              required
            />

            <GlassInput
              label={`${t('onboarding.occupation', 'Occupation / Trade')} *`}
              placeholder="e.g. Construction Worker / Mason"
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
              required
            />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <GlassInput
                type="number"
                label={`${t('onboarding.annualIncome', 'Annual Household Income (₹)')} *`}
                placeholder="120000"
                value={annualIncome}
                onChange={(e) => setAnnualIncome(e.target.value)}
                required
              />
              <GlassInput
                label="Employer / Contractor"
                placeholder="Contractor Firm"
                value={employerType}
                onChange={(e) => setEmployerType(e.target.value)}
              />
            </div>
          </div>
        )}

        {step === 4 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h2 style={{ fontSize: 17, color: 'var(--gold-primary)', margin: 0 }}>
              4. {t('onboarding.step4', 'Household Structure')}
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <GlassInput
                type="number"
                label={t('onboarding.householdMembers', 'Household Members')}
                value={householdMembers}
                onChange={(e) => setHouseholdMembers(e.target.value)}
              />
              <GlassInput
                type="number"
                label={t('onboarding.dependents', 'Dependents')}
                value={dependents}
                onChange={(e) => setDependents(e.target.value)}
              />
            </div>

            <div
              style={{
                background: 'rgba(56, 189, 248, 0.08)',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                borderRadius: 14,
                padding: '14px',
              }}
            >
              <p style={{ margin: 0, fontSize: 12.5, color: '#cbd5e1', lineHeight: 1.5 }}>
                ℹ️ This statutory information determines eligibility for BOCW pensions, PDS Food Security, PM-JAY Ayushman Bharat, and state welfare programs.
              </p>
            </div>
          </div>
        )}

        {/* Step Navigation Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 22 }}>
          {step > 1 ? (
            <GlassButton
              type="button"
              variant="secondary"
              size="md"
              fullWidth={false}
              onClick={handleBack}
            >
              ← {t('common.back', 'Back')}
            </GlassButton>
          ) : (
            <div />
          )}

          {step < 4 ? (
            <GlassButton
              type="button"
              variant="primary"
              size="md"
              fullWidth={false}
              onClick={handleNext}
            >
              {t('common.next', 'Continue')} →
            </GlassButton>
          ) : (
            <GlassButton
              type="button"
              variant="primary"
              size="md"
              fullWidth={false}
              loading={isSubmitting}
              onClick={handleComplete}
            >
              {t('onboarding.complete', 'Save & Start Exploring')} ✓
            </GlassButton>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
