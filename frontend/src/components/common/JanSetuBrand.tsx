import React from 'react';
import { useI18n } from '../../i18n/I18nContext';

export interface JanSetuBrandProps {
  variant?: 'full' | 'compact' | 'icon';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showTagline?: boolean;
  tagline?: string;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
  orientation?: 'vertical' | 'horizontal';
}

export function JanSetuBrand({
  variant = 'full',
  size = 'md',
  showTagline = true,
  tagline,
  className = '',
  style,
  onClick,
  orientation,
}: JanSetuBrandProps) {
  const { language } = useI18n();

  const defaultTagline =
    tagline ||
    (language === 'hi'
      ? 'खोजें • सत्यापित करें • कार्यवाही करें • सुरक्षित रखें'
      : 'DISCOVER. VERIFY. ACT. PROTECT.');

  // Dimensions & typography metrics
  const config = {
    sm: {
      logoSize: 32,
      font: 20,
      subFont: 9,
      gap: 8,
      padding: '4px 6px',
    },
    md: {
      logoSize: 48,
      font: 26,
      subFont: 10,
      gap: 10,
      padding: '6px 10px',
    },
    lg: {
      logoSize: 72,
      font: 32,
      subFont: 11.5,
      gap: 12,
      padding: '8px 14px',
    },
    xl: {
      logoSize: 96,
      font: 38,
      subFont: 13,
      gap: 14,
      padding: '12px 18px',
    },
  }[size];

  // Default orientation based on variant
  const isHorizontal = orientation
    ? orientation === 'horizontal'
    : variant === 'compact';

  // 1. Icon-only variant
  if (variant === 'icon') {
    return (
      <div
        className={`jansetu-brand jansetu-brand-icon ${className} ${onClick ? 'interactive' : ''}`}
        onClick={onClick}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: onClick ? 'pointer' : 'default',
          userSelect: 'none',
          ...style,
        }}
      >
        <img
          src="/brand/jansetu-logo-master.png"
          alt="JanSetu"
          width={config.logoSize}
          height={config.logoSize}
          style={{
            width: config.logoSize,
            height: config.logoSize,
            objectFit: 'contain',
            filter: 'drop-shadow(0 4px 16px rgba(245, 158, 11, 0.22))',
            borderRadius: config.logoSize > 40 ? 12 : 8,
          }}
          loading="eager"
        />
      </div>
    );
  }

  // 2. Compact variant (Logo + JanSetu wordmark)
  if (variant === 'compact') {
    return (
      <div
        className={`jansetu-brand jansetu-brand-compact ${className} ${onClick ? 'interactive' : ''}`}
        onClick={onClick}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        style={{
          display: 'inline-flex',
          flexDirection: isHorizontal ? 'row' : 'column',
          alignItems: 'center',
          gap: config.gap,
          cursor: onClick ? 'pointer' : 'default',
          userSelect: 'none',
          ...style,
        }}
      >
        <img
          src="/brand/jansetu-logo-master.png"
          alt="JanSetu"
          width={config.logoSize}
          height={config.logoSize}
          style={{
            width: config.logoSize,
            height: config.logoSize,
            objectFit: 'contain',
            filter: 'drop-shadow(0 2px 10px rgba(245, 158, 11, 0.20))',
            flexShrink: 0,
          }}
          loading="eager"
        />
        <div
          style={{
            fontFamily: "'Outfit', 'Noto Sans', sans-serif",
            fontSize: config.font,
            fontWeight: 700,
            letterSpacing: '-0.02em',
            color: '#FFFFFF',
            lineHeight: 1.1,
            textShadow: '0 2px 8px rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'baseline',
          }}
        >
          <span>Jan</span>
          <span style={{ color: '#F3C77C' }}>Setu</span>
        </div>
      </div>
    );
  }

  // 3. Full variant (Official Logo + JanSetu + Sovereign Tagline)
  return (
    <div
      className={`jansetu-brand jansetu-brand-full ${className} ${onClick ? 'interactive' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={{
        display: 'inline-flex',
        flexDirection: isHorizontal ? 'row' : 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        gap: config.gap,
        cursor: onClick ? 'pointer' : 'default',
        userSelect: 'none',
        ...style,
      }}
    >
      <div
        style={{
          position: 'relative',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Subtle atmospheric ambient glow behind the official logo mark */}
        <div
          style={{
            position: 'absolute',
            width: config.logoSize * 1.25,
            height: config.logoSize * 1.25,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(245, 158, 11, 0.18) 0%, rgba(10, 14, 23, 0) 70%)',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />
        <img
          src="/brand/jansetu-logo-master.png"
          alt="JanSetu"
          width={config.logoSize}
          height={config.logoSize}
          style={{
            width: config.logoSize,
            height: config.logoSize,
            objectFit: 'contain',
            filter: 'drop-shadow(0 6px 20px rgba(0, 0, 0, 0.6)) drop-shadow(0 0 12px rgba(245, 158, 11, 0.25))',
            position: 'relative',
            zIndex: 1,
            borderRadius: config.logoSize > 48 ? 16 : 10,
          }}
          loading="eager"
        />
      </div>

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: isHorizontal ? 'flex-start' : 'center',
        }}
      >
        {/* JanSetu Wordmark */}
        <div
          style={{
            fontFamily: "'Outfit', 'Noto Sans', sans-serif",
            fontSize: config.font,
            fontWeight: 800,
            letterSpacing: '-0.02em',
            color: '#FFFFFF',
            lineHeight: 1.1,
            textShadow: '0 2px 10px rgba(0,0,0,0.6)',
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
              fontSize: config.subFont,
              fontWeight: 600,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: '#F5C77C',
              opacity: 0.9,
              marginTop: 4,
              textAlign: isHorizontal ? 'left' : 'center',
            }}
          >
            {defaultTagline}
          </div>
        )}
      </div>
    </div>
  );
}

