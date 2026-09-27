import React from 'react';
import { useI18n } from '../../i18n/I18nContext';

interface JanSetuLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showTagline?: boolean;
  tagline?: string;
  className?: string;
  onClick?: () => void;
}

export function JanSetuLogo({
  size = 'md',
  showTagline = true,
  tagline,
  className = '',
  onClick,
}: JanSetuLogoProps) {
  const { language } = useI18n();

  const defaultTagline =
    tagline ||
    (language === 'hi'
      ? 'खोजें • सत्यापित करें • कार्यवाही करें • सुरक्षित रखें'
      : 'DISCOVER. VERIFY. ACT. PROTECT.');

  const sizeMap = {
    sm: { height: 32, font: 20, archWidth: 52, archHeight: 18, subFont: 8.5 },
    md: { height: 48, font: 28, archWidth: 84, archHeight: 26, subFont: 10 },
    lg: { height: 64, font: 38, archWidth: 114, archHeight: 34, subFont: 11.5 },
  };

  const current = sizeMap[size];

  return (
    <div
      className={`jansetu-brand-logo ${className} ${onClick ? 'interactive' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: onClick ? 'pointer' : 'default',
        userSelect: 'none',
      }}
    >
      {/* Arch Bridge / Radiant Arc */}
      <svg
        width={current.archWidth}
        height={current.archHeight}
        viewBox="0 0 100 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ marginBottom: size === 'sm' ? -2 : -4 }}
      >
        <defs>
          <linearGradient id="logoArcGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#F59E0B" stopOpacity="0.2" />
            <stop offset="30%" stopColor="#F5C77C" stopOpacity="0.9" />
            <stop offset="50%" stopColor="#FEF08A" stopOpacity="1" />
            <stop offset="70%" stopColor="#F5C77C" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#F59E0B" stopOpacity="0.2" />
          </linearGradient>
          <filter id="logoGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.5" result="glow" />
            <feMerge>
              <feMergeNode in="glow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Luminous Arch Path */}
        <path
          d="M 6,30 Q 50,4 94,30"
          stroke="url(#logoArcGrad)"
          strokeWidth="3.5"
          strokeLinecap="round"
          filter="url(#logoGlow)"
        />

        {/* Connected Radiant Bridge Nodes */}
        <circle cx="24" cy="21" r="2" fill="#FDE68A" />
        <circle cx="37" cy="14" r="2.5" fill="#FDE68A" />
        <circle cx="50" cy="10" r="3.2" fill="#FFFFFF" filter="url(#logoGlow)" />
        <circle cx="63" cy="14" r="2.5" fill="#FDE68A" />
        <circle cx="76" cy="21" r="2" fill="#FDE68A" />
      </svg>

      {/* Brand Title */}
      <div
        style={{
          fontFamily: "'Outfit', 'Noto Sans', sans-serif",
          fontSize: current.font,
          fontWeight: 700,
          letterSpacing: '-0.02em',
          color: '#FFFFFF',
          lineHeight: 1.1,
          textShadow: '0 2px 10px rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'baseline',
        }}
      >
        <span>Jan</span>
        <span style={{ color: '#F3C77C' }}>Setu</span>
      </div>

      {/* Sovereign Tagline: Discover. Verify. Act. Protect. */}
      {showTagline && (
        <div
          style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: current.subFont,
            fontWeight: 600,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: '#F5C77C',
            opacity: 0.9,
            marginTop: 4,
            textAlign: 'center',
          }}
        >
          {defaultTagline}
        </div>
      )}
    </div>
  );
}
