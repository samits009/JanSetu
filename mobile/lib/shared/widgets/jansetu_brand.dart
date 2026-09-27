import 'package:flutter/material.dart';
import '../../core/theme/tokens.dart';

enum JanSetuBrandVariant {
  full,
  compact,
  icon,
}

enum JanSetuBrandSize {
  sm,
  md,
  lg,
  xl,
}

class JanSetuBrand extends StatelessWidget {
  final JanSetuBrandVariant variant;
  final JanSetuBrandSize size;
  final bool showTagline;
  final String? customTagline;
  final VoidCallback? onTap;

  const JanSetuBrand({
    super.key,
    this.variant = JanSetuBrandVariant.full,
    this.size = JanSetuBrandSize.md,
    this.showTagline = true,
    this.customTagline,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final double logoDim = switch (size) {
      JanSetuBrandSize.sm => 32.0,
      JanSetuBrandSize.md => 48.0,
      JanSetuBrandSize.lg => 72.0,
      JanSetuBrandSize.xl => 96.0,
    };

    final double titleFontSize = switch (size) {
      JanSetuBrandSize.sm => 18.0,
      JanSetuBrandSize.md => 22.0,
      JanSetuBrandSize.lg => 28.0,
      JanSetuBrandSize.xl => 34.0,
    };

    final double subFontSize = switch (size) {
      JanSetuBrandSize.sm => 8.5,
      JanSetuBrandSize.md => 9.5,
      JanSetuBrandSize.lg => 11.0,
      JanSetuBrandSize.xl => 12.5,
    };

    final isHindi = Localizations.localeOf(context).languageCode == 'hi';
    final tagline = customTagline ??
        (isHindi
            ? 'खोजें • सत्यापित करें • कार्यवाही करें • सुरक्षित रखें'
            : 'DISCOVER. VERIFY. ACT. PROTECT.');

    Widget logoImage = Container(
      width: logoDim,
      height: logoDim,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(logoDim > 40 ? 14 : 8),
        boxShadow: [
          BoxShadow(
            color: JanSetuTokens.goldPrimary.withOpacity(0.25),
            blurRadius: 16,
            spreadRadius: 1,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(logoDim > 40 ? 14 : 8),
        child: Image.asset(
          'assets/branding/jansetu-logo.png',
          width: logoDim,
          height: logoDim,
          fit: BoxFit.contain,
          filterQuality: FilterQuality.high,
          errorBuilder: (context, error, stackTrace) {
            // Graceful fallback if asset loading is delayed
            return Container(
              color: const Color(0xFF060A12),
              child: const Icon(
                Icons.shield_outlined,
                color: JanSetuTokens.goldPrimary,
              ),
            );
          },
        ),
      ),
    );

    // 1. Icon variant
    if (variant == JanSetuBrandVariant.icon) {
      if (onTap != null) {
        return GestureDetector(onTap: onTap, child: logoImage);
      }
      return logoImage;
    }

    // 2. Compact variant (Horizontal: Logo + JanSetu)
    if (variant == JanSetuBrandVariant.compact) {
      final content = Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          logoImage,
          const SizedBox(width: 10),
          _buildWordmark(titleFontSize),
        ],
      );

      if (onTap != null) {
        return GestureDetector(onTap: onTap, child: content);
      }
      return content;
    }

    // 3. Full variant (Official Logo + JanSetu + Tagline)
    final content = Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            // Ambient warm gold glow ring
            Container(
              width: logoDim * 1.3,
              height: logoDim * 1.3,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    JanSetuTokens.goldPrimary.withOpacity(0.18),
                    JanSetuTokens.goldPrimary.withOpacity(0.0),
                  ],
                ),
              ),
            ),
            logoImage,
          ],
        ),
        const SizedBox(height: 12),
        _buildWordmark(titleFontSize),
        if (showTagline) ...[
          const SizedBox(height: 5),
          Text(
            tagline,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: JanSetuTokens.goldLight,
              fontSize: subFontSize,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
            ),
          ),
        ],
      ],
    );

    if (onTap != null) {
      return GestureDetector(onTap: onTap, child: content);
    }
    return content;
  }

  Widget _buildWordmark(double fontSize) {
    return ShaderMask(
      shaderCallback: (bounds) => const LinearGradient(
        colors: [Color(0xFFFFFFFF), Color(0xFFF3C77C)],
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
      ).createShader(bounds),
      child: Text(
        'JanSetu',
        style: TextStyle(
          color: Colors.white,
          fontSize: fontSize,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.2,
        ),
      ),
    );
  }
}
