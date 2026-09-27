import React, { useEffect } from 'react';

export interface GlassDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  children: React.ReactNode;
  position?: 'right' | 'bottom';
  className?: string;
}

export function GlassDrawer({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  position = 'right',
  className = '',
}: GlassDrawerProps) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    }
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="glass-drawer-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
    >
      <div className={`glass-drawer-panel glass-drawer-${position} ${className}`}>
        {/* Drawer Header */}
        <div className="glass-drawer-header">
          <div>
            {title && <h3 className="glass-drawer-title">{title}</h3>}
            {subtitle && <p className="glass-drawer-subtitle">{subtitle}</p>}
          </div>

          <button
            type="button"
            className="glass-drawer-close-btn"
            onClick={onClose}
            aria-label="Close drawer"
          >
            ×
          </button>
        </div>

        {/* Drawer Body */}
        <div className="glass-drawer-body">{children}</div>
      </div>
    </div>
  );
}
