import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useI18n } from '../../i18n/I18nContext';

interface LanguageSelectorProps {
  className?: string;
  variant?: 'pill' | 'capsule' | 'icon';
}

export function LanguageSelector({ className = '', variant = 'pill' }: LanguageSelectorProps) {
  const { language, setLanguage } = useI18n();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close on click outside or touch outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent | TouchEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

  // Keyboard navigation support (Escape to close)
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      } else if (e.key === 'ArrowDown' || e.key === 'Enter') {
        if (!isOpen) setIsOpen(true);
      }
    },
    [isOpen]
  );

  const handleSelect = (lang: 'en' | 'hi') => {
    setLanguage(lang);
    setIsOpen(false);
  };

  return (
    <div
      ref={containerRef}
      className={`glass-lang-selector-wrapper ${className}`}
      style={{ position: 'relative' }}
      onKeyDown={handleKeyDown}
    >
      {/* Collapsed Glass Capsule: Globe + Active Language + Toggle Chevron */}
      <button
        type="button"
        className="glass-lang-capsule-btn"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label="Select Sovereign Language"
      >
        <span className="lang-globe-icon" aria-hidden="true">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
        </span>
        <span className="lang-active-code">{language === 'hi' ? 'हिंदी' : 'EN'}</span>
        <span className="lang-chevron-icon" aria-hidden="true" style={{ transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s ease' }}>
          ▾
        </span>
      </button>

      {/* Floating Frosted Glass Language Popover Menu */}
      {isOpen && (
        <div
          className="glass-lang-popover"
          role="listbox"
          aria-label="Language options"
        >
          <div className="glass-popover-header">
            <span>Select Language / भाषा चुनें</span>
          </div>

          <button
            type="button"
            role="option"
            aria-selected={language === 'en'}
            className={`glass-lang-item ${language === 'en' ? 'selected' : ''}`}
            onClick={() => handleSelect('en')}
          >
            <div className="lang-item-labels">
              <span className="lang-item-main">English</span>
              <span className="lang-item-sub">Default statutory locale</span>
            </div>
            {language === 'en' && (
              <span className="lang-gold-check" aria-hidden="true">
                ✓
              </span>
            )}
          </button>

          <button
            type="button"
            role="option"
            aria-selected={language === 'hi'}
            className={`glass-lang-item ${language === 'hi' ? 'selected' : ''}`}
            onClick={() => handleSelect('hi')}
          >
            <div className="lang-item-labels">
              <span className="lang-item-main">हिन्दी</span>
              <span className="lang-item-sub">राजभाषा (Devanagari)</span>
            </div>
            {language === 'hi' && (
              <span className="lang-gold-check" aria-hidden="true">
                ✓
              </span>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
