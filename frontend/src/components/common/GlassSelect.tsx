import React, { useState, useRef, useEffect, useMemo, useId } from 'react';
import { useI18n } from '../../i18n/I18nContext';

export interface GlassSelectOption {
  label: string;
  value: string;
  subLabel?: string;
  disabled?: boolean;
}

export interface GlassSelectGroup {
  label: string;
  options: GlassSelectOption[];
}

export interface GlassSelectProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (event: { target: { value: string; name?: string } }) => void;
  onSelect?: (value: string) => void;
  options?: GlassSelectOption[];
  groups?: GlassSelectGroup[];
  disabled?: boolean;
  required?: boolean;
  error?: string;
  name?: string;
  id?: string;
  className?: string;
  searchable?: boolean;
  searchPlaceholder?: string;
  emptyText?: string;
  leftIcon?: React.ReactNode;
}

export function GlassSelect({
  label,
  placeholder,
  value,
  onChange,
  onSelect,
  options,
  groups,
  disabled = false,
  required = false,
  error,
  name,
  id,
  className = '',
  searchable,
  searchPlaceholder,
  emptyText,
  leftIcon,
}: GlassSelectProps) {
  const { language } = useI18n();
  const generatedId = useId();
  const instanceId = id || `glass-select-${generatedId}`;
  const listboxId = `${instanceId}-listbox`;

  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [openUpward, setOpenUpward] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const listboxRef = useRef<HTMLDivElement>(null);

  // Flatten options for total count & easy lookup
  const allOptions = useMemo<GlassSelectOption[]>(() => {
    if (groups && groups.length > 0) {
      return groups.flatMap((g) => g.options);
    }
    return options || [];
  }, [groups, options]);

  // Find currently selected option object
  const selectedOption = useMemo(() => {
    return allOptions.find((opt) => opt.value === value);
  }, [allOptions, value]);

  // Determine whether search should be enabled (auto-enabled if >6 items or explicitly true)
  const isSearchEnabled = searchable !== undefined ? searchable : allOptions.length > 6;

  // Filtered groups / options based on search query
  const filteredGroups = useMemo(() => {
    if (!groups) return null;
    const query = searchQuery.trim().toLowerCase();
    if (!query) return groups;

    return groups
      .map((group) => ({
        ...group,
        options: group.options.filter(
          (opt) =>
            opt.label.toLowerCase().includes(query) ||
            (opt.subLabel && opt.subLabel.toLowerCase().includes(query)) ||
            opt.value.toLowerCase().includes(query)
        ),
      }))
      .filter((group) => group.options.length > 0);
  }, [groups, searchQuery]);

  const filteredOptions = useMemo(() => {
    if (groups) {
      return filteredGroups ? filteredGroups.flatMap((g) => g.options) : [];
    }
    const query = searchQuery.trim().toLowerCase();
    if (!query) return options || [];
    return (options || []).filter(
      (opt) =>
        opt.label.toLowerCase().includes(query) ||
        (opt.subLabel && opt.subLabel.toLowerCase().includes(query)) ||
        opt.value.toLowerCase().includes(query)
    );
  }, [groups, filteredGroups, options, searchQuery]);

  // Close dropdown on outside click
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Close when another dropdown opens
  useEffect(() => {
    const handleOtherDropdownOpen = (e: Event) => {
      const customEvent = e as CustomEvent<{ id: string }>;
      if (customEvent.detail && customEvent.detail.id !== instanceId) {
        setIsOpen(false);
      }
    };

    window.addEventListener('jansetu-dropdown-open', handleOtherDropdownOpen);
    return () => window.removeEventListener('jansetu-dropdown-open', handleOtherDropdownOpen);
  }, [instanceId]);

  // Compute opening direction (upward vs downward)
  useEffect(() => {
    if (isOpen && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;
      setOpenUpward(spaceBelow < 280 && spaceAbove > spaceBelow);

      // Focus search input on open
      if (isSearchEnabled) {
        setTimeout(() => {
          searchInputRef.current?.focus();
        }, 30);
      }
    } else {
      setSearchQuery('');
      setHighlightedIndex(0);
    }
  }, [isOpen, isSearchEnabled]);

  // Trigger dropdown toggle
  const toggleDropdown = () => {
    if (disabled) return;
    const nextState = !isOpen;
    if (nextState) {
      window.dispatchEvent(
        new CustomEvent('jansetu-dropdown-open', { detail: { id: instanceId } })
      );
    }
    setIsOpen(nextState);
  };

  // Option selection
  const handleSelectOption = (opt: GlassSelectOption) => {
    if (opt.disabled) return;
    if (onChange) {
      onChange({ target: { value: opt.value, name } });
    }
    if (onSelect) {
      onSelect(opt.value);
    }
    setIsOpen(false);
    triggerRef.current?.focus();
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (!isOpen) {
          toggleDropdown();
        } else if (filteredOptions[highlightedIndex]) {
          handleSelectOption(filteredOptions[highlightedIndex]);
        }
        break;

      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          toggleDropdown();
        } else {
          setHighlightedIndex((prev) =>
            prev < filteredOptions.length - 1 ? prev + 1 : 0
          );
        }
        break;

      case 'ArrowUp':
        e.preventDefault();
        if (!isOpen) {
          toggleDropdown();
        } else {
          setHighlightedIndex((prev) =>
            prev > 0 ? prev - 1 : filteredOptions.length - 1
          );
        }
        break;

      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        triggerRef.current?.focus();
        break;

      case 'Home':
        if (isOpen) {
          e.preventDefault();
          setHighlightedIndex(0);
        }
        break;

      case 'End':
        if (isOpen) {
          e.preventDefault();
          setHighlightedIndex(Math.max(0, filteredOptions.length - 1));
        }
        break;

      case 'Tab':
        setIsOpen(false);
        break;
    }
  };

  // Localized placeholders
  const resolvedPlaceholder =
    placeholder || (language === 'hi' ? '-- चयन करें --' : '-- Select an option --');
  const resolvedSearchPlaceholder =
    searchPlaceholder ||
    (language === 'hi' ? 'सूची में खोजें...' : 'Search options...');
  const resolvedEmptyText =
    emptyText ||
    (language === 'hi' ? 'कोई परिणाम नहीं मिला' : 'No matching results found');

  return (
    <div
      ref={containerRef}
      className={`glass-select-wrapper ${error ? 'has-error' : ''} ${className}`}
      onKeyDown={handleKeyDown}
    >
      {/* Hidden input to preserve standard form submission & programmatic inspection */}
      <input type="hidden" name={name} value={value || ''} />

      {/* Label */}
      {label && (
        <label
          htmlFor={instanceId}
          className="glass-input-label"
          onClick={() => triggerRef.current?.focus()}
        >
          {label}
        </label>
      )}

      {/* Custom Closed Capsule Trigger */}
      <button
        ref={triggerRef}
        id={instanceId}
        type="button"
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls={listboxId}
        aria-disabled={disabled}
        aria-required={required}
        disabled={disabled}
        className={`glass-select-trigger ${isOpen ? 'is-open' : ''} ${
          disabled ? 'is-disabled' : ''
        }`}
        onClick={toggleDropdown}
      >
        <div className="glass-select-content-preview">
          {leftIcon && <div className="glass-input-icon-left">{leftIcon}</div>}

          {selectedOption ? (
            <span className="glass-select-value-text">{selectedOption.label}</span>
          ) : (
            <span className="glass-select-placeholder-text">
              {resolvedPlaceholder}
            </span>
          )}
        </div>

        {/* Gold Chevron Indicator with 180deg Rotation */}
        <div className={`glass-select-chevron ${isOpen ? 'is-open' : ''}`}>
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>

      {/* Floating Glassmorphic Popover Menu */}
      {isOpen && (
        <div
          className={`glass-select-popover ${openUpward ? 'open-upward' : ''}`}
          role="dialog"
          aria-modal="false"
        >
          {/* Instant Search Bar */}
          {isSearchEnabled && (
            <div className="glass-select-search-box">
              <span className="glass-select-search-icon">🔍</span>
              <input
                ref={searchInputRef}
                type="text"
                className="glass-select-search-input"
                placeholder={resolvedSearchPlaceholder}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onClick={(e) => e.stopPropagation()}
              />
              {searchQuery && (
                <button
                  type="button"
                  className="glass-select-clear-btn"
                  onClick={() => setSearchQuery('')}
                  title="Clear search"
                  aria-label="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
          )}

          {/* Custom Listbox */}
          <div
            ref={listboxRef}
            id={listboxId}
            role="listbox"
            tabIndex={-1}
            className="glass-select-listbox"
          >
            {/* Render Grouped Options */}
            {filteredGroups && filteredGroups.length > 0 ? (
              filteredGroups.map((group, gIdx) => (
                <div key={gIdx} className="glass-select-group-block">
                  <div className="glass-select-group-header">
                    <span>{group.label}</span>
                    <span style={{ fontSize: 10, opacity: 0.6 }}>
                      {group.options.length}
                    </span>
                  </div>

                  {group.options.map((opt) => {
                    const isSelected = opt.value === value;
                    const flatIdx = filteredOptions.indexOf(opt);
                    const isHighlighted = flatIdx === highlightedIndex;

                    return (
                      <div
                        key={opt.value}
                        role="option"
                        aria-selected={isSelected}
                        className={`glass-select-option ${
                          isSelected ? 'is-selected' : ''
                        } ${isHighlighted ? 'is-highlighted' : ''}`}
                        onClick={() => handleSelectOption(opt)}
                        onMouseEnter={() => setHighlightedIndex(flatIdx)}
                      >
                        <div className="glass-select-option-main">
                          <span>{opt.label}</span>
                          {opt.subLabel && (
                            <small className="glass-select-option-sub">
                              {opt.subLabel}
                            </small>
                          )}
                        </div>

                        {isSelected && (
                          <span className="glass-select-check">✓</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))
            ) : filteredOptions.length > 0 ? (
              filteredOptions.map((opt, oIdx) => {
                const isSelected = opt.value === value;
                const isHighlighted = oIdx === highlightedIndex;

                return (
                  <div
                    key={opt.value}
                    role="option"
                    aria-selected={isSelected}
                    className={`glass-select-option ${
                      isSelected ? 'is-selected' : ''
                    } ${isHighlighted ? 'is-highlighted' : ''}`}
                    onClick={() => handleSelectOption(opt)}
                    onMouseEnter={() => setHighlightedIndex(oIdx)}
                  >
                    <div className="glass-select-option-main">
                      <span>{opt.label}</span>
                      {opt.subLabel && (
                        <small className="glass-select-option-sub">
                          {opt.subLabel}
                        </small>
                      )}
                    </div>

                    {isSelected && (
                      <span className="glass-select-check">✓</span>
                    )}
                  </div>
                );
              })
            ) : (
              /* Localized Empty State */
              <div className="glass-select-empty">
                <span style={{ fontSize: 18, color: 'var(--gold-primary)' }}>
                  ✦
                </span>
                <span>{resolvedEmptyText}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Field Error Message */}
      {error && (
        <div className="glass-input-error" role="alert">
          <span>⚠</span> {error}
        </div>
      )}
    </div>
  );
}
