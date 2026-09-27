import 'package:flutter/material.dart';

/// JANSETU Sovereign Design Tokens
/// Exact 1:1 match with web frontend reference system (styles.css)
class JanSetuTokens {
  JanSetuTokens._();

  // Core Backgrounds
  static const Color bgDeep = Color(0xFF060A12);
  static const Color bgNavy = Color(0xFF090E1A);
  static const Color bgSurface = Color(0xFF0D1527);
  static const Color bgGlassPrimary = Color(0xB80D1424); // rgba(13, 20, 36, 0.72)
  static const Color bgGlassSecondary = Color(0x99131D33); // rgba(19, 29, 51, 0.60)
  static const Color bgGlassTertiary = Color(0x0DFFFFFF); // rgba(255, 255, 255, 0.05)

  // Glass Borders & Outlines
  static const Color glassBorder = Color(0x1FFFFFFF); // rgba(255, 255, 255, 0.12)
  static const Color glassBorderSubtle = Color(0x12FFFFFF); // rgba(255, 255, 255, 0.07)
  static const Color glassBorderFocus = Color(0xA6F5C77C); // rgba(245, 199, 124, 0.65)
  static const Color glassHighlight = Color(0x26FFFFFF); // rgba(255, 255, 255, 0.15)

  // Primary Luminous Accent: Warm Champagne Gold / Amber
  static const Color goldPrimary = Color(0xFFF5C77C);
  static const Color goldLight = Color(0xFFFCE7A9);
  static const Color goldDark = Color(0xFFE5A952);
  static const Color goldGlow = Color(0x66F5C77C);
  static const Color goldTextOnBtn = Color(0xFF140E05);

  // Status & Feature Colors
  static const Color skyPrimary = Color(0xFF38BDF8);
  static const Color skyGlow = Color(0x5938BDF8);
  static const Color emeraldPrimary = Color(0xFF10B981);
  static const Color emeraldGlow = Color(0x5910B981);
  static const Color amberPrimary = Color(0xFFF59E0B);
  static const Color amberGlow = Color(0x59F59E0B);
  static const Color rosePrimary = Color(0xFFF43F5E);
  static const Color roseGlow = Color(0x59F43F5E);

  // Typography Colors
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);
  static const Color textGold = Color(0xFFF5C77C);

  // Gradients
  static const LinearGradient goldGradient = LinearGradient(
    colors: [goldLight, goldPrimary, goldDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient glassGradient = LinearGradient(
    colors: [
      Color(0xCC0D1527),
      Color(0x99090E1A),
    ],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient atmosphericGradient = LinearGradient(
    colors: [
      Color(0xFF060A12),
      Color(0xFF090E1A),
      Color(0xFF0D1527),
      Color(0xFF060A12),
    ],
    stops: [0.0, 0.35, 0.7, 1.0],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  // Shadows
  static const List<BoxShadow> glassShadow = [
    BoxShadow(
      color: Color(0x80000000),
      offset: Offset(0, 16),
      blurRadius: 36,
      spreadRadius: -4,
    ),
  ];

  static const List<BoxShadow> goldGlowShadow = [
    BoxShadow(
      color: Color(0x59F5C77C),
      offset: Offset(0, 6),
      blurRadius: 20,
      spreadRadius: -2,
    ),
  ];
}
