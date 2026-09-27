import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'tokens.dart';

class JanSetuTheme {
  JanSetuTheme._();

  static ThemeData get darkTheme {
    final baseTextTheme = Typography.material2021().white;
    final displayFont = GoogleFonts.outfitTextTheme(baseTextTheme);
    final bodyFont = GoogleFonts.notoSansTextTheme(baseTextTheme);

    final textTheme = displayFont.copyWith(
      displayLarge: displayFont.displayLarge?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.5,
      ),
      displayMedium: displayFont.displayMedium?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.5,
      ),
      headlineLarge: displayFont.headlineLarge?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontWeight: FontWeight.w700,
      ),
      headlineMedium: displayFont.headlineMedium?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontWeight: FontWeight.w600,
      ),
      headlineSmall: displayFont.headlineSmall?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontWeight: FontWeight.w600,
      ),
      titleLarge: displayFont.titleLarge?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontWeight: FontWeight.w600,
      ),
      titleMedium: displayFont.titleMedium?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontWeight: FontWeight.w500,
      ),
      titleSmall: displayFont.titleSmall?.copyWith(
        color: JanSetuTokens.textSecondary,
        fontWeight: FontWeight.w500,
      ),
      bodyLarge: bodyFont.bodyLarge?.copyWith(
        color: JanSetuTokens.textPrimary,
        fontSize: 16,
        height: 1.5,
      ),
      bodyMedium: bodyFont.bodyMedium?.copyWith(
        color: JanSetuTokens.textSecondary,
        fontSize: 14,
        height: 1.5,
      ),
      bodySmall: bodyFont.bodySmall?.copyWith(
        color: JanSetuTokens.textMuted,
        fontSize: 12,
        height: 1.4,
      ),
      labelLarge: displayFont.labelLarge?.copyWith(
        color: JanSetuTokens.goldTextOnBtn,
        fontWeight: FontWeight.w600,
        fontSize: 15,
        letterSpacing: 0.2,
      ),
    );

    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: JanSetuTokens.bgDeep,
      primaryColor: JanSetuTokens.goldPrimary,
      canvasColor: JanSetuTokens.bgNavy,
      textTheme: textTheme,
      colorScheme: const ColorScheme.dark(
        primary: JanSetuTokens.goldPrimary,
        secondary: JanSetuTokens.skyPrimary,
        surface: JanSetuTokens.bgSurface,
        error: JanSetuTokens.rosePrimary,
        onPrimary: JanSetuTokens.goldTextOnBtn,
        onSecondary: Colors.white,
        onSurface: JanSetuTokens.textPrimary,
        onError: Colors.white,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: displayFont.titleLarge?.copyWith(
          color: JanSetuTokens.textPrimary,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.2,
        ),
        iconTheme: const IconThemeData(color: JanSetuTokens.textPrimary),
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: Colors.transparent,
        modalBackgroundColor: Colors.transparent,
        elevation: 0,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: JanSetuTokens.bgGlassSecondary,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        hintStyle: bodyFont.bodyMedium?.copyWith(color: JanSetuTokens.textMuted),
        labelStyle: bodyFont.bodyMedium?.copyWith(color: JanSetuTokens.textSecondary),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: JanSetuTokens.glassBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: JanSetuTokens.glassBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: JanSetuTokens.glassBorderFocus, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: JanSetuTokens.rosePrimary),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: JanSetuTokens.rosePrimary, width: 1.5),
        ),
      ),
    );
  }
}
