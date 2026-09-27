import 'dart:ui';
import 'package:flutter/material.dart';
import '../../core/theme/tokens.dart';

class CinematicScaffold extends StatelessWidget {
  final Widget body;
  final PreferredSizeWidget? appBar;
  final Widget? bottomNavigationBar;
  final bool showBridgeMotif;

  const CinematicScaffold({
    super.key,
    required this.body,
    this.appBar,
    this.bottomNavigationBar,
    this.showBridgeMotif = true,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: JanSetuTokens.bgDeep,
      appBar: appBar,
      bottomNavigationBar: bottomNavigationBar,
      body: Stack(
        children: [
          // 1. Deep Midnight Horizon Gradient
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: JanSetuTokens.atmosphericGradient,
              ),
            ),
          ),

          // 2. Luminous Ambient Glows (India Horizon)
          Positioned(
            top: -120,
            right: -80,
            child: Container(
              width: 320,
              height: 320,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    JanSetuTokens.goldPrimary.withOpacity(0.12),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 60,
            left: -100,
            child: Container(
              width: 360,
              height: 360,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    JanSetuTokens.skyPrimary.withOpacity(0.08),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),

          // 3. Setu Bridge Architectural Motif
          if (showBridgeMotif)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              height: 180,
              child: CustomPaint(
                painter: _BridgeMotifPainter(),
              ),
            ),

          // 4. Subtle blur layer
          Positioned.fill(
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 0.5, sigmaY: 0.5),
              child: const SizedBox.expand(),
            ),
          ),

          // 5. Foregound Content
          SafeArea(child: body),
        ],
      ),
    );
  }
}

class _BridgeMotifPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          JanSetuTokens.goldPrimary.withOpacity(0.06),
          Colors.transparent,
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    // Elegant Setu curved arches
    final path = Path();
    path.moveTo(0, size.height * 0.95);
    path.quadraticBezierTo(
      size.width * 0.25,
      size.height * 0.45,
      size.width * 0.5,
      size.height * 0.65,
    );
    path.quadraticBezierTo(
      size.width * 0.75,
      size.height * 0.85,
      size.width,
      size.height * 0.35,
    );
    canvas.drawPath(path, paint);

    // Secondary subtle arch
    final path2 = Path();
    path2.moveTo(0, size.height * 0.8);
    path2.quadraticBezierTo(
      size.width * 0.5,
      size.height * 0.2,
      size.width,
      size.height * 0.7,
    );
    canvas.drawPath(path2, paint..strokeWidth = 0.8);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
