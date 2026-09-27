import React, { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import {
  CinematicBackground,
  JanSetuLogo,
  JanSetuBrand,
  LanguageSelector,
  GlassButton,
  GlassDrawer,
  AgentActivity,
} from './common';

export function Layout({ children }: { children: React.ReactNode }) {
  const { language, t } = useI18n();
  const { user, currentCitizenId, logout } = useAuth();
  const [agentDrawerOpen, setAgentDrawerOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Close profile dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navItems = [
    {
      to: '/',
      label: t('nav.home', 'Home'),
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
      ),
    },
    {
      to: '/benefits',
      label: t('nav.benefits', 'Benefits'),
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      ),
    },
    {
      to: '/documents',
      label: t('nav.documents', 'Documents'),
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
      ),
    },
    {
      to: '/applications',
      label: t('nav.applications', 'Applications'),
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 11 12 14 22 4" />
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
        </svg>
      ),
    },
    {
      to: '/profile',
      label: t('nav.profile', 'Profile'),
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      ),
    },
  ];

  const getInitials = (name?: string, email?: string) => {
    if (name && name.trim()) {
      const parts = name.trim().split(' ');
      if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
      return parts[0].slice(0, 2).toUpperCase();
    }
    if (email) return email.slice(0, 2).toUpperCase();
    return 'JS';
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  const citizenDisplayName = user?.name || user?.email?.split('@')[0] || 'Citizen';

  return (
    <div className="app-shell">
      {/* 1. Cinematic Ambient Background Layer */}
      <CinematicBackground showBridgePath={true} intensity="subtle" />

      {/* 2. Desktop Glass Sidebar Navigation (≥ 900px) */}
      <aside className="desktop-sidebar">
        <div style={{ padding: '8px 12px 16px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <JanSetuBrand variant="full" size="sm" showTagline={true} onClick={() => navigate('/')} />
        </div>

        <nav className="sidebar-nav-list" aria-label="Desktop Primary Navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Desktop Quick Agent Trigger */}
        <div style={{ marginTop: 'auto', paddingTop: 16 }}>
          <button
            type="button"
            className="glass-btn glass-btn-secondary glass-btn-sm glass-btn-full"
            onClick={() => setAgentDrawerOpen(true)}
            style={{ fontSize: 13, gap: 8 }}
          >
            <span>✦</span>
            <span>Ask JanSetu AI</span>
          </button>
        </div>
      </aside>

      {/* 3. Frosted Glass Topbar */}
      <header className="app-topbar">
        <div className="topbar-brand" onClick={() => navigate('/')}>
          <JanSetuBrand variant="compact" size="sm" />
        </div>

        <div className="topbar-actions" ref={menuRef}>
          {/* Segmented Language Selector */}
          <LanguageSelector />

          {/* Persistent Welfare Notifications */}
          <div style={{ position: 'relative' }} ref={notifRef}>
            <button
              type="button"
              className="topbar-icon-pill"
              onClick={() => setNotificationsOpen((o) => !o)}
              aria-label="Welfare Notifications"
              style={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid var(--glass-border)',
                display: 'grid',
                placeItems: 'center',
                color: 'var(--text-primary)',
                position: 'relative',
                cursor: 'pointer',
              }}
            >
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              <span
                style={{
                  position: 'absolute',
                  top: 7,
                  right: 7,
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: 'var(--gold-primary)',
                  boxShadow: '0 0 8px rgba(245, 199, 124, 0.8)',
                }}
              />
            </button>

            {/* Notifications Dropdown Panel */}
            {notificationsOpen && (
              <div
                className="glass-lang-dropdown"
                style={{ top: 48, right: 0, minWidth: 290, padding: '14px 16px' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10, paddingBottom: 6, borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                  <strong style={{ fontSize: 13, color: 'var(--text-primary)' }}>
                    {language === 'hi' ? 'कल्याण सूचनाएं' : 'Welfare Alerts'}
                  </strong>
                  <span className="status-pill status-pill-green status-pill-sm">
                    {language === 'hi' ? 'सक्रिय' : 'Active'}
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ padding: '8px 10px', borderRadius: 12, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
                    <small style={{ color: 'var(--gold-primary)', fontWeight: 700, display: 'block', fontSize: 11.5 }}>
                      ✓ {language === 'hi' ? 'नागरिक सत्र सत्यापित' : 'Citizen Session Verified'}
                    </small>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                      {language === 'hi'
                        ? 'आपका संप्रभु प्रोफ़ाइल सुरक्षित डेटाबेस से संबद्ध है।'
                        : 'Your sovereign profile is verified and connected to statutory welfare intelligence.'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Citizen Avatar Capsule */}
          <button
            type="button"
            className="citizen-avatar-pill"
            onClick={() => setUserMenuOpen((o) => !o)}
            aria-label="Citizen Account Menu"
          >
            <span className="citizen-avatar-badge">{getInitials(user?.name, user?.email)}</span>
            <span style={{ maxWidth: 90, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {citizenDisplayName}
            </span>
            <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>▼</span>
          </button>

          {/* User Profile Dropdown Menu */}
          {userMenuOpen && (
            <div className="glass-lang-dropdown" style={{ top: 50, right: 0, minWidth: 220 }}>
              <div style={{ padding: '8px 12px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <strong style={{ display: 'block', fontSize: 14, color: 'var(--text-primary)' }}>
                  {citizenDisplayName}
                </strong>
                <small style={{ color: 'var(--text-muted)', fontSize: 11, wordBreak: 'break-all' }}>
                  {user?.email}
                </small>
              </div>

              <button
                type="button"
                className="glass-lang-option"
                onClick={() => {
                  setUserMenuOpen(false);
                  navigate('/profile');
                }}
              >
                <span>👤 {t('nav.profile', 'Profile')}</span>
              </button>

              <button
                type="button"
                className="glass-lang-option"
                onClick={() => {
                  setUserMenuOpen(false);
                  navigate('/onboarding');
                }}
              >
                <span>✏️ {language === 'hi' ? 'नागरिक प्रोफ़ाइल सेटअप' : 'Profile Setup'}</span>
              </button>

              <div style={{ height: 1, background: 'rgba(255,255,255,0.08)', margin: '4px 0' }} />

              <button
                type="button"
                className="glass-lang-option"
                onClick={handleLogout}
                style={{ color: '#f87171' }}
              >
                <span>⎋ {t('nav.logout', 'Log Out')}</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* 4. Page Content Container */}
      <main className="content-wrap">{children}</main>

      {/* 5. Global Floating "Ask JanSetu" Trigger Pill */}
      <button
        type="button"
        className="ask-jansetu-fab"
        onClick={() => setAgentDrawerOpen(true)}
        aria-label="Ask JanSetu Agent"
      >
        <span style={{ color: 'var(--gold-primary)' }}>✦</span>
        <span>{language === 'hi' ? 'पूछें जनसेतु' : 'Ask JanSetu'}</span>
      </button>

      {/* 6. Agent Activity Glass Drawer (No generic chat; Safe Execution Summaries) */}
      <GlassDrawer
        isOpen={agentDrawerOpen}
        onClose={() => setAgentDrawerOpen(false)}
        title={language === 'hi' ? 'जनसेतु स्वायत्त एजेंट' : 'JanSetu Sovereign Agent'}
        subtitle={language === 'hi' ? 'सुरक्षित कल्याण निरंतरता सहायक' : 'Autonomous Welfare Assistant'}
        position="right"
      >
        <AgentActivity citizenId={currentCitizenId} />
      </GlassDrawer>

      {/* 7. Bottom Navigation (Mobile Primary < 900px) */}
      <nav className="glass-bottom-nav" aria-label="Mobile Bottom Navigation">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-tab-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-tab-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
