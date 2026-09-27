import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import {
  CinematicBackground,
  JanSetuLogo,
  JanSetuBrand,
  LanguageSelector,
  GlassCard,
  GlassInput,
  GlassButton,
} from '../components/common';

type AuthMode = 'login' | 'register' | 'forgot' | 'link_google';

export function Login() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [identifier, setIdentifier] = useState(''); // Email or Mobile for login
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pendingSub, setPendingSub] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resetSuccessMessage, setResetSuccessMessage] = useState<string | null>(null);

  const { login, register, linkGoogle, continueWithGoogle } = useAuth();
  const { language, t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/';

  // Parse URL query parameters for OAuth callbacks and errors
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const errParam = params.get('error');
    const modeParam = params.get('mode');
    const emailParam = params.get('email');
    const subParam = params.get('pending_sub');

    if (emailParam) {
      setEmail(emailParam);
      setIdentifier(emailParam);
    }
    if (subParam) {
      setPendingSub(subParam);
    }

    if (modeParam === 'link_google' || errParam === 'account_linking_required') {
      setMode('link_google');
      setError(
        language === 'hi'
          ? `इस ईमेल (${emailParam || ''}) के साथ एक जनसेतु खाता पहले से मौजूद है। अपने गूगल खाते को लिंक करने के लिए कृपया अपना पासवर्ड दर्ज करें।`
          : `An existing JanSetu account was found for ${emailParam || 'this email'}. Please enter your password to link your Google account securely.`
      );
    } else if (errParam === 'google_cancelled') {
      setError(language === 'hi' ? 'गूगल साइन-इन रद्द कर दिया गया।' : 'Google sign-in was cancelled.');
    } else if (errParam === 'invalid_state') {
      setError(language === 'hi' ? 'अमान्य सुरक्षा स्थिति। कृपया पुनः प्रयास करें।' : 'Invalid security state. Please try again.');
    } else if (errParam === 'google_config_missing') {
      setError(
        language === 'hi'
          ? 'सर्वर पर गूगल साइन-इन अभी कॉन्फ़िगर नहीं है। कृपया ईमेल और मोबाइल नंबर से पंजीकरण करें।'
          : 'Google sign-in is not yet configured on this server. Please create an account with email and mobile.'
      );
    } else if (errParam === 'google_auth_failed') {
      setError(language === 'hi' ? 'गूगल प्रमाणीकरण विफल रहा।' : 'Google authentication failed. Please try again.');
    }
  }, [location.search, language]);

  const handleModeSwitch = (newMode: AuthMode) => {
    setMode(newMode);
    setError(null);
    setResetSuccessMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResetSuccessMessage(null);

    // 1. Password Reset Mode
    if (mode === 'forgot') {
      if (!identifier.trim()) {
        setError(language === 'hi' ? 'कृपया ईमेल या मोबाइल नंबर दर्ज करें' : 'Please enter your email or mobile number');
        return;
      }
      setResetSuccessMessage(
        language === 'hi'
          ? 'यदि यह संपर्क पंजीकृत है, तो पासवर्ड रीसेट निर्देश आपके पंजीकृत ईमेल/मोबाइल पर भेज दिए गए हैं।'
          : 'If this contact is registered, password recovery instructions have been dispatched.'
      );
      return;
    }

    // 2. Safe Google Account Linking Mode
    if (mode === 'link_google') {
      if (!password) {
        setError(language === 'hi' ? 'कृपया अपना जनसेतु पासवर्ड दर्ज करें' : 'Please enter your JanSetu password');
        return;
      }
      setIsSubmitting(true);
      try {
        const profile = await linkGoogle(email, password, pendingSub);
        if (profile.onboarding_completed) {
          navigate('/', { replace: true });
        } else {
          navigate('/onboarding', { replace: true });
        }
      } catch (err: any) {
        setError(err?.message || (language === 'hi' ? 'खाता लिंक करना विफल रहा।' : 'Account linking failed.'));
      } finally {
        setIsSubmitting(false);
      }
      return;
    }

    // 3. Normal Registration Mode
    if (mode === 'register') {
      if (!name.trim()) {
        setError(language === 'hi' ? 'कृपया अपना पूरा नाम दर्ज करें' : 'Please enter your full name');
        return;
      }
      if (!email.trim() || !email.includes('@')) {
        setError(language === 'hi' ? 'कृपया एक वैध ईमेल पता दर्ज करें' : 'Please enter a valid email address');
        return;
      }
      if (!mobileNumber.trim()) {
        setError(language === 'hi' ? 'कृपया अपना 10 अंकों का मोबाइल नंबर दर्ज करें' : 'Please enter your 10-digit mobile number');
        return;
      }
      if (password.length < 8) {
        setError(t('auth.errorShortPass', 'Password must be at least 8 characters long'));
        return;
      }
      if (password !== confirmPassword) {
        setError(t('auth.errorMismatch', 'Passwords do not match'));
        return;
      }
      if (!agreedToTerms) {
        setError(language === 'hi' ? 'कृपया सेवा की शर्तों और गोपनीयता नीति को स्वीकार करें' : 'Please agree to the Terms of Service & Privacy Policy');
        return;
      }

      setIsSubmitting(true);
      try {
        await register({
          name: name.trim(),
          email: email.trim(),
          mobile_number: mobileNumber.trim(),
          password,
          confirm_password: confirmPassword,
          preferred_language: language as 'en' | 'hi',
        });
        // Registration takes new user to Onboarding
        navigate('/onboarding', { replace: true });
      } catch (err: any) {
        setError(err?.message || (language === 'hi' ? 'पंजीकरण विफल रहा।' : 'Registration failed.'));
      } finally {
        setIsSubmitting(false);
      }
      return;
    }

    // 4. Login Mode (Email or Mobile Number)
    if (mode === 'login') {
      if (!identifier.trim()) {
        setError(language === 'hi' ? 'कृपया ईमेल या मोबाइल नंबर दर्ज करें' : 'Please enter your email or mobile number');
        return;
      }
      if (!password) {
        setError(language === 'hi' ? 'कृपया अपना पासवर्ड दर्ज करें' : 'Please enter your password');
        return;
      }

      setIsSubmitting(true);
      try {
        const profile = await login(identifier.trim(), password);
        // Returning user redirect: if onboarding is complete -> Home, else -> Onboarding
        if (!profile.onboarding_completed || profile.requires_mobile) {
          navigate('/onboarding', { replace: true });
        } else {
          navigate(from === '/login' || from === '/register' ? '/' : from, { replace: true });
        }
      } catch (err: any) {
        setError(err?.message || (language === 'hi' ? 'अमान्य क्रेडेंशियल्स।' : 'Invalid credentials.'));
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  // SVGs
  const userIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );

  const mailIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  );

  const phoneIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );

  const lockIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );

  const googleIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" style={{ flexShrink: 0 }}>
      <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
      <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
      <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
      <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
    </svg>
  );

  return (
    <div className="auth-page">
      {/* 1. Cinematic Background with Setu Bridge & Atmospheric Depth */}
      <CinematicBackground showBridgePath={true} intensity="high" />

      {/* 2. Top Bar: Back Button (if register/forgot/link) + Unified Top-Right Glass Cluster */}
      <header className="auth-top-bar">
        {mode !== 'login' ? (
          <button
            type="button"
            className="auth-back-btn"
            onClick={() => handleModeSwitch('login')}
            aria-label="Back to Login"
            title="Back to Login"
          >
            ‹
          </button>
        ) : (
          <div /> /* Spacer */
        )}

        <div className="auth-control-cluster">
          <LanguageSelector />
          <button
            type="button"
            className="glass-circle-btn"
            aria-label="Information & Help"
            title={language === 'hi' ? 'जनसेतु सहायता' : 'JanSetu Help'}
            onClick={() => alert(language === 'hi' ? 'जनसेतु: नागरिक कल्याण और योजनाओं की सुरक्षित निरंतरता प्रणाली।' : 'JanSetu: Sovereign Citizen Welfare & Continuity Platform.')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4" />
              <path d="M12 8h.01" />
            </svg>
          </button>
        </div>
      </header>

      {/* 3. Centered Floating Frosted Glass Auth Card */}
      <main className="auth-card-container">
        <GlassCard className="auth-card" variant="default">
          {/* Brand Logo & Sovereign Tagline */}
          <div className="auth-header">
            <JanSetuBrand variant="full" size="lg" showTagline={true} />

            {/* Screen Titles */}
            {mode === 'login' && (
              <>
                <h1 className="auth-title">
                  {language === 'hi' ? 'वापसी पर स्वागत है' : 'Welcome Back'}
                </h1>
                <p className="auth-subtitle">
                  {language === 'hi' ? 'अपनी जनसेतु यात्रा जारी रखें।' : 'Continue your JanSetu journey.'}
                </p>
              </>
            )}

            {mode === 'register' && (
              <>
                <h1 className="auth-title">
                  {language === 'hi' ? 'खाता बनाएं' : 'Create Account'}
                </h1>
                <p className="auth-subtitle">
                  {language === 'hi'
                    ? 'कल्याणकारी अवसरों को खोजने और प्रबंधित करने के लिए जनसेतु से जुड़ें।'
                    : 'Join JanSetu to discover and manage welfare opportunities.'}
                </p>
              </>
            )}

            {mode === 'link_google' && (
              <>
                <h1 className="auth-title">
                  {language === 'hi' ? 'गूगल खाता लिंक करें' : 'Link Google Account'}
                </h1>
                <p className="auth-subtitle">
                  {language === 'hi'
                    ? 'सुरक्षा सत्यापन के लिए अपना जनसेतु पासवर्ड दर्ज करें।'
                    : 'Enter your JanSetu password to link your Google identity securely.'}
                </p>
              </>
            )}

            {mode === 'forgot' && (
              <>
                <h1 className="auth-title">
                  {language === 'hi' ? 'पासवर्ड रीसेट करें' : 'Reset Password'}
                </h1>
                <p className="auth-subtitle">
                  {language === 'hi'
                    ? 'जारी रखने के लिए अपना ईमेल या मोबाइल नंबर दर्ज करें।'
                    : 'Enter your email or mobile number to continue.'}
                </p>
              </>
            )}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="glass-input-error" style={{ marginBottom: 16, fontSize: 13 }} role="alert">
              <span>⚠</span>
              <span>{error}</span>
            </div>
          )}

          {/* Reset Success Message */}
          {resetSuccessMessage && (
            <div
              style={{
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                borderRadius: 14,
                padding: '12px 16px',
                color: '#34d399',
                fontSize: 13,
                marginBottom: 16,
              }}
            >
              ✓ {resetSuccessMessage}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="auth-form" noValidate>
            {/* REGISTER MODE FIELDS */}
            {mode === 'register' && (
              <>
                {/* 1. Full Name */}
                <GlassInput
                  type="text"
                  placeholder={language === 'hi' ? 'पूरा नाम' : 'Full Name'}
                  leftIcon={userIcon}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  autoComplete="name"
                  required
                />

                {/* 2. Email Address */}
                <GlassInput
                  type="email"
                  placeholder={language === 'hi' ? 'ईमेल पता' : 'Email Address'}
                  leftIcon={mailIcon}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />

                {/* 3. Mobile Number */}
                <GlassInput
                  type="tel"
                  placeholder={language === 'hi' ? 'मोबाइल नंबर (उदा. 9876543210)' : 'Mobile Number (e.g. +91 98765 43210)'}
                  leftIcon={phoneIcon}
                  value={mobileNumber}
                  onChange={(e) => setMobileNumber(e.target.value)}
                  autoComplete="tel"
                  required
                />

                {/* 4. Password */}
                <GlassInput
                  isPassword={true}
                  placeholder={language === 'hi' ? 'पासवर्ड (न्यूनतम 8 वर्ण)' : 'Password (min. 8 characters)'}
                  leftIcon={lockIcon}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                  required
                />

                {/* 5. Confirm Password */}
                <GlassInput
                  isPassword={true}
                  placeholder={language === 'hi' ? 'पासवर्ड की पुष्टि करें' : 'Confirm Password'}
                  leftIcon={lockIcon}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  autoComplete="new-password"
                  required
                />

                {/* Terms of Service & Privacy Policy */}
                <label className="auth-checkbox-label" style={{ fontSize: 12.5, lineHeight: 1.4, margin: '4px 0 8px 0' }}>
                  <input
                    type="checkbox"
                    checked={agreedToTerms}
                    onChange={(e) => setAgreedToTerms(e.target.checked)}
                  />
                  <span>
                    {language === 'hi' ? (
                      <>मैं <span style={{ color: 'var(--gold-primary)' }}>सेवा की शर्तों</span> और <span style={{ color: 'var(--gold-primary)' }}>गोपनीयता नीति</span> से सहमत हूँ</>
                    ) : (
                      <>I agree to the <span style={{ color: 'var(--gold-primary)' }}>Terms of Service</span> and <span style={{ color: 'var(--gold-primary)' }}>Privacy Policy</span></>
                    )}
                  </span>
                </label>

                {/* Primary CTA: Create Account */}
                <GlassButton
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={isSubmitting}
                  style={{ marginTop: 4 }}
                >
                  {language === 'hi' ? 'खाता बनाएं' : 'Create Account'}
                </GlassButton>

                {/* Divider: OR */}
                <div className="auth-divider" style={{ margin: '14px 0' }}>
                  <span>{language === 'hi' ? 'या' : 'OR'}</span>
                </div>

                {/* Continue with Google Button */}
                <GlassButton
                  type="button"
                  variant="secondary"
                  size="lg"
                  onClick={continueWithGoogle}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 10,
                    width: '100%',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.18)',
                    color: '#f8fafc',
                    fontWeight: 500,
                  }}
                >
                  {googleIcon}
                  <span>{language === 'hi' ? 'गूगल के साथ जारी रखें' : 'Continue with Google'}</span>
                </GlassButton>
              </>
            )}

            {/* LOGIN MODE FIELDS */}
            {mode === 'login' && (
              <>
                {/* Email or Mobile Number */}
                <GlassInput
                  type="text"
                  placeholder={language === 'hi' ? 'ईमेल या मोबाइल नंबर' : 'Email or Mobile Number'}
                  leftIcon={mailIcon}
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  autoComplete="username"
                  required
                />

                {/* Password */}
                <GlassInput
                  isPassword={true}
                  placeholder={language === 'hi' ? 'अपना पासवर्ड दर्ज करें' : 'Password'}
                  leftIcon={lockIcon}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />

                {/* Remember Me & Forgot Password */}
                <div className="auth-controls-row">
                  <label className="auth-checkbox-label">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                    />
                    <span>{language === 'hi' ? 'मुझे याद रखें' : 'Remember me'}</span>
                  </label>

                  <button
                    type="button"
                    className="auth-footer-link"
                    style={{ background: 'none', border: 'none', padding: 0 }}
                    onClick={() => handleModeSwitch('forgot')}
                  >
                    {language === 'hi' ? 'पासवर्ड भूल गए?' : 'Forgot Password?'}
                  </button>
                </div>

                {/* Primary CTA: Log In */}
                <GlassButton
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={isSubmitting}
                  style={{ marginTop: 4 }}
                >
                  {language === 'hi' ? 'लॉग इन करें' : 'Log In'}
                </GlassButton>

                {/* Divider: OR */}
                <div className="auth-divider" style={{ margin: '14px 0' }}>
                  <span>{language === 'hi' ? 'या' : 'OR'}</span>
                </div>

                {/* Continue with Google Button */}
                <GlassButton
                  type="button"
                  variant="secondary"
                  size="lg"
                  onClick={continueWithGoogle}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 10,
                    width: '100%',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.18)',
                    color: '#f8fafc',
                    fontWeight: 500,
                  }}
                >
                  {googleIcon}
                  <span>{language === 'hi' ? 'गूगल के साथ जारी रखें' : 'Continue with Google'}</span>
                </GlassButton>
              </>
            )}

            {/* LINK GOOGLE ACCOUNT MODE */}
            {mode === 'link_google' && (
              <>
                <GlassInput
                  type="email"
                  placeholder={language === 'hi' ? 'ईमेल पता' : 'Email Address'}
                  leftIcon={mailIcon}
                  value={email}
                  disabled={true}
                  required
                />

                <GlassInput
                  isPassword={true}
                  placeholder={language === 'hi' ? 'जनसेतु खाता पासवर्ड' : 'JanSetu Account Password'}
                  leftIcon={lockIcon}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />

                <GlassButton
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={isSubmitting}
                  style={{ marginTop: 8 }}
                >
                  {language === 'hi' ? 'सत्यापित करें और खाता लिंक करें' : 'Verify & Link Google Account'}
                </GlassButton>

                <div className="auth-divider" style={{ margin: '14px 0' }}>
                  <span>{language === 'hi' ? 'या' : 'OR'}</span>
                </div>

                <GlassButton
                  type="button"
                  variant="secondary"
                  size="md"
                  onClick={() => handleModeSwitch('login')}
                >
                  {language === 'hi' ? 'रद्द करें और लॉग इन करें' : 'Cancel & Return to Login'}
                </GlassButton>
              </>
            )}

            {/* FORGOT PASSWORD MODE */}
            {mode === 'forgot' && (
              <>
                <GlassInput
                  type="text"
                  placeholder={language === 'hi' ? 'ईमेल या मोबाइल नंबर' : 'Email or Mobile Number'}
                  leftIcon={mailIcon}
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  autoComplete="username"
                  required
                />

                <GlassButton
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={isSubmitting}
                  style={{ marginTop: 8 }}
                >
                  {language === 'hi' ? 'जारी रखें' : 'Continue'}
                </GlassButton>

                <div className="auth-divider" style={{ margin: '14px 0' }}>
                  <span>{language === 'hi' ? 'या' : 'OR'}</span>
                </div>

                <GlassButton
                  type="button"
                  variant="secondary"
                  size="md"
                  onClick={() => handleModeSwitch('login')}
                >
                  {language === 'hi' ? 'लॉग इन पर वापस जाएं' : 'Back to Login'}
                </GlassButton>
              </>
            )}
          </form>

          {/* Footer Switching Prompt */}
          <footer className="auth-footer" style={{ marginTop: 18 }}>
            {mode === 'login' && (
              <p>
                {language === 'hi' ? 'खाता नहीं है? ' : "Don't have an account? "}
                <button
                  type="button"
                  className="auth-footer-link"
                  onClick={() => handleModeSwitch('register')}
                >
                  {language === 'hi' ? 'खाता बनाएं' : 'Create an account'}
                </button>
              </p>
            )}

            {mode === 'register' && (
              <p>
                {language === 'hi' ? 'क्या आपके पास पहले से खाता है? ' : 'Already have an account? '}
                <button
                  type="button"
                  className="auth-footer-link"
                  onClick={() => handleModeSwitch('login')}
                >
                  {language === 'hi' ? 'लॉग इन करें' : 'Log in'}
                </button>
              </p>
            )}
          </footer>
        </GlassCard>
      </main>
    </div>
  );
}
