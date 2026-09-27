import React, { useEffect, useRef } from 'react';
import { GlassCard } from './GlassCard';

export interface GlassModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  closeOnBackdrop?: boolean;
}

export function GlassModal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
  size = 'md',
  className = '',
  closeOnBackdrop = true,
}: GlassModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
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
      className="glass-modal-backdrop"
      onClick={(e) => {
        if (closeOnBackdrop && e.target === e.currentTarget) {
          onClose();
        }
      }}
      role="dialog"
      aria-modal="true"
    >
      <div className={`glass-modal-container glass-modal-${size} ${className}`} ref={modalRef}>
        <GlassCard variant="luminous" className="glass-modal-card">
          {/* Modal Header */}
          <div className="glass-modal-header">
            <div>
              {title && <h3 className="glass-modal-title">{title}</h3>}
              {subtitle && <p className="glass-modal-subtitle">{subtitle}</p>}
            </div>

            <button
              type="button"
              className="glass-modal-close-btn"
              onClick={onClose}
              aria-label="Close dialog"
            >
              ×
            </button>
          </div>

          {/* Modal Body */}
          <div className="glass-modal-body">{children}</div>

          {/* Modal Footer */}
          {footer && <div className="glass-modal-footer">{footer}</div>}
        </GlassCard>
      </div>
    </div>
  );
}
