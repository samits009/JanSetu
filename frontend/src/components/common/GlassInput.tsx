import React, { useState } from 'react';

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  error?: string;
  isPassword?: boolean;
}

export function GlassInput({
  label,
  leftIcon,
  rightIcon,
  error,
  isPassword,
  type = 'text',
  className = '',
  id,
  ...rest
}: GlassInputProps) {
  const [showPassword, setShowPassword] = useState(false);
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;
  const inputId = id || (label ? `input-${label.toLowerCase().replace(/\s+/g, '-')}` : undefined);

  return (
    <div className={`glass-input-wrapper ${error ? 'has-error' : ''} ${className}`}>
      {label && (
        <label htmlFor={inputId} className="glass-input-label">
          {label}
        </label>
      )}

      <div className="glass-input-capsule">
        {leftIcon && <div className="glass-input-icon-left">{leftIcon}</div>}

        <input
          id={inputId}
          type={inputType}
          className="glass-input-field"
          {...rest}
        />

        {isPassword ? (
          <button
            type="button"
            className="glass-input-icon-right glass-eye-btn"
            onClick={() => setShowPassword(p => !p)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            tabIndex={-1}
          >
            {showPassword ? (
              /* Eye Off */
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            ) : (
              /* Eye */
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        ) : (
          rightIcon && <div className="glass-input-icon-right">{rightIcon}</div>
        )}
      </div>

      {error && (
        <div className="glass-input-error" role="alert">
          <span>⚠</span> {error}
        </div>
      )}
    </div>
  );
}
