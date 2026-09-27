import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import {
  CinematicBackground,
  JanSetuLogo,
  LanguageSelector,
  GlassCard,
  GlassInput,
  GlassButton,
} from '../components/common';

type AuthMode = 'login' | 'register' | 'forgot';

export function Login() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resetSuccessMessage, setResetSuccessMessage] = useState<string | null>(null);

  const { login, register } = useAuth();
  const { language, t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/';

  const handleModeSwitch = (newMode: AuthMode) => {
    setMode(newMode);
    setError(null);
    setResetSuccessMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResetSuccessMessage(null);

    // Validation
    if (mode === 'forgot') {
      if (!email.trim()) {
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

    if (!email || !password) {
      setError(t('auth.errorRequired', 'Please fill in all mandatory fields'));
      return;
    }

    if (mode === 'register') {
      if (!name.trim()) {
        setError(language === 'hi' ? 'कृपया अपना पूरा नाम दर्ज करें' : 'Please enter your full name');
        return;
      }
      if (password.length < 8) {
        setError(t('auth.errorShortPass', 'Password must be at least 8 characters'));
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
    }

    setIsSubmitting(true);
    try {
      if (mode === 'register') {
        await register({
          email,
          password,
          name: name.trim(),
          preferred_language: language,
        });
        navigate('/onboarding', { replace: true });
      } else {
        await login(email, password);
        navigate(from === '/login' || from === '/register' ? '/' : from, { replace: true });
      }
    } catch (err: any) {
      setError(
        err?.message ||
          (mode === 'register'
            ? language === 'hi'
              ? 'पंजीकरण विफल रहा। ईमेल पहले से उपयोग में हो सकता है।'
              : 'Registration failed. Email may already be in use.'
            : language === 'hi'
            ? 'अमान्य क्रेडेंशियल्स। कृपया ईमेल और पासवर्ड की जांच करें।'
            : 'Invalid credentials. Please verify your email and password.')
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // SVG Icons
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

  const lockIcon = (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );

  return (
    <div className="auth-page">
      {/* 1. Cinematic Background with Setu Bridge & Atmospheric Depth */}
      <CinematicBackground showBridgePath={true} intensity="high" />

      {/* 2. Top Bar: Back Button (if register/forgot) + Unified Top-Right Glass Cluster */}
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
            onClick={() => alert(language === 'hi' ? 'जनसेतु: नागरिक कल्याण और योजनाओं की सुरक्षित निरंतरता प्रणाली।' : 'JanSetu: Citizen Welfare Continuity & Sovereign Sovereign Bridge.')}
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
            <JanSetuLogo size="md" showTagline={true} />

            {/* Dynamic Screen Titles strictly following Section 12 specifications */}
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
            {/* Full Name (Register Mode Only) */}
            {mode === 'register' && (
              <GlassInput
                type="text"
                placeholder={language === 'hi' ? 'पूरा नाम' : 'Full Name'}
                leftIcon={userIcon}
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
                required
              />
            )}

            {/* Email or Mobile Number */}
            <GlassInput
              type="text"
              placeholder={language === 'hi' ? 'ईमेल या मोबाइल नंबर' : 'Email or Mobile Number'}
              leftIcon={mailIcon}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
            />

            {/* Password (Login & Register Modes) */}
            {mode !== 'forgot' && (
              <GlassInput
                isPassword={true}
                placeholder={
                  mode === 'register'
                    ? language === 'hi'
                      ? 'पासवर्ड बनाएं (न्यूनतम 8 वर्ण)'
                      : 'Create a password'
                    : language === 'hi'
                    ? 'अपना पासवर्ड दर्ज करें'
                    : 'Enter your password'
                }
                leftIcon={lockIcon}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
                required
              />
            )}

            {/* Confirm Password (Register Mode Only) */}
            {mode === 'register' && (
              <GlassInput
                isPassword={true}
                placeholder={language === 'hi' ? 'पासवर्ड की पुष्टि करें' : 'Confirm password'}
                leftIcon={lockIcon}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
                required
              />
            )}

            {/* Remember Me & Forgot Password (Login Mode Only) */}
            {mode === 'login' && (
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
            )}

            {/* Terms of Service & Privacy Policy (Register Mode Only) */}
            {mode === 'register' && (
              <label className="auth-checkbox-label" style={{ fontSize: 12.5, lineHeight: 1.4 }}>
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
            )}

            {/* Primary Luminous CTA Button - Warm gold, clear text, no '—' or '→' (Section 11) */}
            <GlassButton
              type="submit"
              variant="primary"
              size="lg"
              loading={isSubmitting}
              style={{ marginTop: 8 }}
            >
              {mode === 'login' && (language === 'hi' ? 'लॉग इन करें' : 'Log In')}
              {mode === 'register' && (language === 'hi' ? 'खाता बनाएं' : 'Create Account')}
              {mode === 'forgot' && (language === 'hi' ? 'जारी रखें' : 'Continue')}
            </GlassButton>

            {/* Back to Login Secondary for Forgot Password */}
            {mode === 'forgot' && (
              <>
                <div className="auth-divider">
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

          {/* Footer Switching Prompt strictly following Section 12 semantics */}
          <footer className="auth-footer">
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
