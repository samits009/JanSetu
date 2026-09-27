---
name: Civic Horizon Dark
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.03em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4rem
  gutter-mobile: 1rem
  gutter-desktop: 1.5rem
  content-max-width: 88rem
---

## Brand & Style

This design system establishes an authoritative, institutional, and precision-engineered digital experience for modern civic technology and public digital infrastructure (DPI). Operating at the intersection of sovereign-grade trust and high-velocity fintech interfaces, the system delivers razor-sharp clarity without visual clutter or decorative distractions.

The visual style is **Corporate Modern with Precision FinTech Minimalism**:
- **Palette Architecture**: Obsidian and charcoal field layers anchored by deep slate foundations, eliminating screen glare while optimizing low-light field visibility.
- **Structural Integrity**: Strict 1px tectonic borders and muted hairline gridlines replace heavy elevation shadows, giving every record, transaction, and biometric verification state a tangible, sovereign weight.
- **Semantic Vividness**: Ultra-deliberate signal tokens (verification emerald, deadline amber, critical crimson, and DPI indigo/cobalt) cut cleanly through dark terrain with mathematical intent.
- **Dual-Script Equilibrium**: Harmonious integration of Latin and Devanagari typography, matching typographic cap-heights, baseline rhythms, and optical weights across languages to treat multilingual civic access as a primary architectural pillar.

## Colors

The system relies on high-contrast, deeply saturated semantic accents resting on structural slate-black canvases. Each surface tier provides sufficient contrast to maintain WCAG 2.1 AAA legibility across civic audits, telemetry dashboards, and transaction feeds.

### Canvas & Surface Architecture
- **Base Canvas (`#0b0f19`)**: Ground zero. Used for full-viewport document backgrounds and root containers.
- **Surface Level 1 (`#111827`)**: Structural modules, persistent sidebars, cards, and primary content slabs.
- **Surface Level 2 (`#1e293b`)**: Interactive surfaces, table header rows, elevated modal dialogs, and nested sub-cards.
- **Surface Level 3 (`#334155`)**: Hover states, active segment pills, and floating action layers.
- **Hairline Structural Border (`#334155`)**: Crisp boundary definition across all containers, inputs, and split views.
- **Subtle Inactive Border (`#1e293b`)**: Low-emphasis structural rules and divider lines.

### Text & Glyph Contrast Tiers
- **Text Primary (`#f8fafc`)**: Top-level headers, active values, metric figures, and imperative commands.
- **Text Secondary (`#cbd5e1`)**: Field labels, metadata attributes, table cells, and narrative body copy.
- **Text Tertiary / Muted (`#64748b`)**: Inactive timestamps, system placeholders, and disabled states.

### Semantic & Agent Accents
- **DPI Agent Cobalt / Indigo (`#3b82f6` / `#6366f1`)**: Primary interaction points, verifiable credential pathways, active AI processing states, and secure cryptographic handshakes.
- **Verified Emerald (`#10b981` / `#059669`)**: Authenticated identities, successful ledger commits, compliant statuses, and confirmed civic benefits.
- **Urgent Amber (`#f59e0b`)**: Time-sensitive filings, grace period countdowns, and pending manual authorizations.
- **Critical Crimson (`#ef4444`)**: Identity revocations, non-compliance alerts, security threshold breaches, and audit failures.

## Typography

Typography reflects strict civic authority, high-density readability, and technical precision.

- **Headings (`Space Grotesk`)**: Provides an authoritative, sharp, geometric presence for KPI panels, sheet titles, and high-level section names.
- **Interface & Reading Body (`Inter`)**: Serves as the primary operational workhorse, offering optimal optical performance for continuous citizen data records, bilingual disclosures, and dense form layouts. When rendering Hindi (Devanagari), use matching weight Noto Sans Devanagari fallbacks aligned directly on optical x-height.
- **System Metrics & Identifiers (`JetBrains Mono`)**: Applied to transaction hashes, Aadhaar/ID maskings, verification timestamps, status tags, and machine-parsed civic ledger values.

### Dual-Script Handling (English / Hindi)
Ensure line-height values maintain at least 1.45x on body containers accommodating Devanagari matras without vertical clipping. Paired English and Hindi labels must align on the shared baseline rather than bounding box centers.

## Layout & Spacing

The layout is built on an architectural 4px/8px modular scale engineered for data-dense governance dashboards and transactional flows.

### Grid Framework
- **Desktop (1280px and above)**: 12-column fluid grid, 24px gutters, max-width constrained to `88rem` (1408px) with auto-centering margins.
- **Tablet (768px - 1279px)**: 8-column responsive grid with 16px gutters and 24px fixed lateral padding.
- **Mobile (below 768px)**: 4-column stack grid with 12px gutters and 16px lateral margins.

### Spatial Rhythms
- Compact micro-spacings (`space-xs` to `space-sm`) define tightly grouped civic status indicators and tabular data cells.
- Structural module gaps (`space-lg` to `space-xl`) separate distinct administrative ledgers and contextual action forms.

## Elevation & Depth

Visual hierarchy does not rely on soft diffuse dropshadows. It is communicated strictly through surface luminosity stepping and crisp border delineation:

- **Level 0 (Base Foundation)**: Canvas color `#0b0f19` with zero elevation and no borders.
- **Level 1 (Card & Module Layer)**: Surface `#111827` encapsulated by a 1px solid border of `#334155`. Flat projection.
- **Level 2 (Active Focus & Flyout Panels)**: Surface `#1e293b` enclosed by `#334155` with an ultra-subtle directional border glow using the active semantic token at 15% alpha.
- **Level 3 (Modals & Overlays)**: Surface `#111827` overlaid with an impenetrable slate backdrop blur (`backdrop-blur-md` over `rgba(11, 15, 25, 0.85)`) framed with a high-contrast `#334155` border.
- **Data Callouts**: Status cards incorporate a left-edge accent border (3px solid in emerald, amber, crimson, or cobalt) with zero drop shadow.

## Shapes

The design system enforces a disciplined, technical geometry with controlled `roundedness: 1` (Soft).

- **Standard Elements (Buttons, Text Inputs, Segment Pickers)**: Fixed at `0.25rem` (4px).
- **Cards, System Slabs, and Modules (`rounded-lg`)**: Fixed at `0.5rem` (8px).
- **Modal Containers & Dialog Sheets (`rounded-xl`)**: Fixed at `0.75rem` (12px).
- **Status Pills, Code Tags, and Identity Badges**: Strict `0.25rem` (4px) or full capsule execution where tracking labels mandate inline compactness.

No large bulbous corners are permitted; all structural elements preserve an architectural, precision-machined edge.

## Components

### Buttons
- **Primary Civic Action**: Background `#3b82f6`, foreground `#f8fafc`, font `JetBrains Mono` 12px/medium, 4px radius, 0.5rem vertical by 1rem horizontal padding. Hover shifts to `#2563eb`. Focus produces a 2px offset ring in `#6366f1`.
- **Secondary Structural**: Background `#1e293b`, border 1px solid `#334155`, text `#f8fafc`. Hover transitions background to `#334155`.
- **Verified / Affirmative**: Background `#059669`, foreground `#ffffff`, used exclusively for identity commitments, claim sign-offs, and final cryptographic authorizations.
- **Critical / Danger**: Background transparent, border 1px solid `#ef4444`, text `#ef4444`. Hover fills with `rgba(239, 68, 68, 0.15)`.

### Chips & Semantic Status Badges
- Built using `JetBrains Mono` uppercase 10px typography, 2px vertical by 6px horizontal padding, 4px corner radius.
- **Verified Chip**: Background `rgba(16, 185, 129, 0.12)`, border 1px solid `rgba(16, 185, 129, 0.4)`, text `#10b981`. Includes a solid 4px green status dot.
- **Urgent Action Chip**: Background `rgba(245, 158, 11, 0.12)`, border 1px solid `rgba(245, 158, 11, 0.4)`, text `#f59e0b`.
- **Risk Alert Chip**: Background `rgba(239, 68, 68, 0.12)`, border 1px solid `rgba(239, 68, 68, 0.4)`, text `#ef4444`.
- **AI / DPI Agent Chip**: Background `rgba(59, 130, 246, 0.15)`, border 1px solid `rgba(99, 102, 241, 0.5)`, text `#93c5fd`.

### Input Fields & Select Controls
- Background `#111827`, border 1px solid `#334155`, corner radius 4px, height 40px, text `#f8fafc`, placeholder `#64748b`.
- On focus: Border color switches directly to `#3b82f6` with an inner hairline highlight.
- Bilingual labels: Display Latin identifier in 12px Inter medium (`#cbd5e1`) followed by Devanagari translation in `#94a3b8`.

### Cards & Telemetry Containers
- Background `#111827`, border 1px solid `#334155`, padding 1.25rem, corner radius 8px.
- Metric cards feature an upper row housing the mono label and semantic status pill, followed by an extra-bold 28px Space Grotesk data point, concluding with an explanatory timestamp in `#64748b`.

### Checkboxes & Radio Buttons
- Checkbox: 16x16px, background `#111827`, border 1px solid `#334155`, 4px radius. Checked state fills `#3b82f6` with an obsidian checkmark.
- Radio: 16x16px circular boundary. Active state displays an interior concentric disk of `#3b82f6` separated by a 2px gap of `#111827`.

### Lists & Ledger Grids
- Alternating or continuous `#111827` surface rows separated by 1px solid `#1e293b` hairlines.
- Padding: 12px vertical by 16px horizontal. Hovering illuminates the row in `#1e293b`.
- Monospaced metadata columns (hashes, dates, transaction IDs) stay consistently right-aligned for instant visual scanning.