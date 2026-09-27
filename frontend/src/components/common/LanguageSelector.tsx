import React, { useState, useRef, useEffect } from 'react';
import { useI18n } from '../../i18n/I18nContext';

interface LanguageSelectorProps {
  className?: string;
  variant?: 'compact' | 'segmented';
}

export function LanguageSelector({ className = '' }: LanguageSelectorProps) {
  const { language, setLanguage } = useI18n();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (lang: 'en' | 'hi') => {
    setLanguage(lang);
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} className={`glass-lang-selector-wrapper ${className}`} style={{ position: 'relative' }}>
      {/* Pill-shaped Segmented Selector (🌐  EN  |  हिंदी) */}
      <div
        className="glass-lang-pill"
        role="group"
        aria-label="Language selection"
      >
        <button
          type="button"
          onClick={() => setIsOpen(prev => !prev)}
          className="lang-globe-icon-btn"
          aria-label="Toggle language menu"
          title="Select Language"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
        </button>

        <button
          type="button"
          onClick={() => handleSelect('en')}
          className={`lang-segment ${language === 'en' ? 'active' : ''}`}
          aria-pressed={language === 'en'}
        >
          EN
        </button>

        <span className="lang-divider">|</span>

        <button
          type="button"
          onClick={() => handleSelect('hi')}
          className={`lang-segment ${language === 'hi' ? 'active' : ''}`}
          aria-pressed={language === 'hi'}
        >
          हिंदी
        </button>
      </div>

      {/* Floating Frosted Glass Language Panel */}
      {isOpen && (
        <div className="glass-lang-dropdown" role="menu">
          <div className="glass-dropdown-header">
            <span>Select Language / भाषा चुनें</span>
          </div>

          <button
            type="button"
            role="menuitem"
            className={`glass-lang-option ${language === 'en' ? 'selected' : ''}`}
            onClick={() => handleSelect('en')}
          >
            <div className="lang-opt-main">
              <span className="lang-name">English</span>
              <span className="lang-sub">English</span>
            </div>
            {language === 'en' && <span className="lang-check">✓</span>}
          </button>

          <button
            type="button"
            role="menuitem"
            className={`glass-lang-option ${language === 'hi' ? 'selected' : ''}`}
            onClick={() => handleSelect('hi')}
          >
            <div className="lang-opt-main">
              <span className="lang-name">हिंदी</span>
              <span className="lang-sub">Hindi</span>
            </div>
            {language === 'hi' && <span className="lang-check">✓</span>}
          </button>
        </div>
      )}
    </div>
  );
}
