import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';
import '../core/localization/app_localizations.dart';
import '../core/repositories/auth_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/jansetu_brand.dart';

// ─── Auth Mode ────────────────────────────────────────────────────────────────
enum _AuthMode { login, register, forgotPassword }

class AuthScreen extends StatefulWidget {
  final AuthRepository authRepository;
  final VoidCallback onAuthenticated;
  final VoidCallback onLanguageToggle;

  const AuthScreen({
    super.key,
    required this.authRepository,
    required this.onAuthenticated,
    required this.onLanguageToggle,
  });

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen>
    with SingleTickerProviderStateMixin {
  _AuthMode _mode = _AuthMode.login;
  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _obscureConfirm = true;
  bool _rememberMe = true;
  String? _errorMessage;

  final _identifierController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  late AnimationController _anim;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _anim = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnim = CurvedAnimation(parent: _anim, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(begin: const Offset(0, 0.06), end: Offset.zero)
        .animate(CurvedAnimation(parent: _anim, curve: Curves.easeOutCubic));
    _anim.forward();
  }

  @override
  void dispose() {
    _anim.dispose();
    _identifierController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _switchMode(_AuthMode mode) {
    _anim.reset();
    setState(() { _mode = mode; _errorMessage = null; });
    _anim.forward();
  }

  Future<void> _handleSubmit() async {
    setState(() => _errorMessage = null);
    final id = _identifierController.text.trim();
    final pw = _passwordController.text;

    if (id.isEmpty || (_mode != _AuthMode.forgotPassword && pw.isEmpty)) {
      setState(() => _errorMessage = 'Please fill in all required fields.');
      return;
    }
    if (_mode != _AuthMode.forgotPassword && pw.length < 8) {
      setState(() => _errorMessage = 'Password must be at least 8 characters.');
      return;
    }
    if (_mode == _AuthMode.register && pw != _confirmPasswordController.text) {
      setState(() => _errorMessage = 'Passwords do not match.');
      return;
    }

    setState(() => _isLoading = true);
    try {
      if (_mode == _AuthMode.login) {
        await widget.authRepository.login(username: id, password: pw);
        widget.onAuthenticated();
      } else if (_mode == _AuthMode.register) {
        final isEmail = id.contains('@');
        await widget.authRepository.register(
          email: isEmail ? id : null,
          phone: !isEmail ? id : null,
          password: pw,
          preferredLanguage: context.l10n.currentLanguageCode,
        );
        widget.onAuthenticated();
      } else {
        await Future.delayed(const Duration(milliseconds: 800));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Reset link sent to your email/phone.')),
          );
          _switchMode(_AuthMode.login);
        }
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('ApiException: ', '').replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final isLogin = _mode == _AuthMode.login;
    final isRegister = _mode == _AuthMode.register;
    final isForgot = _mode == _AuthMode.forgotPassword;

    return Scaffold(
      backgroundColor: JanSetuTokens.bgDeep,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // ── 1. Atmospheric background ──────────────────────────────────────
          const _AtmosphericBackground(),

          // ── 2. Top bar with language toggle ───────────────────────────────
          SafeArea(
            child: Align(
              alignment: Alignment.topRight,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: _TopBar(
                  isHindi: l10n.isHindi,
                  onLanguageToggle: widget.onLanguageToggle,
                ),
              ),
            ),
          ),

          // ── 3. Main card ───────────────────────────────────────────────────
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
                child: FadeTransition(
                  opacity: _fadeAnim,
                  child: SlideTransition(
                    position: _slideAnim,
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 400),
                      child: _AuthCard(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Logo
                            const _JanSetuLogo(),
                            const SizedBox(height: 20),

                            // Title
                            Text(
                              isForgot
                                  ? (l10n.isHindi ? 'पासवर्ड रीसेट करें' : 'Reset Password')
                                  : isLogin
                                      ? (l10n.isHindi ? 'वापसी पर स्वागत है' : 'Welcome Back')
                                      : (l10n.isHindi ? 'खाता बनाएं' : 'Create Account'),
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                color: JanSetuTokens.textPrimary,
                                fontSize: 22,
                                fontWeight: FontWeight.w700,
                                letterSpacing: -0.3,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              isForgot
                                  ? (l10n.isHindi
                                      ? 'जारी रखने के लिए अपना ईमेल या मोबाइल नंबर दर्ज करें।'
                                      : 'Enter your email or mobile number to continue.')
                                  : isLogin
                                      ? (l10n.isHindi
                                          ? 'अपनी जनसेतु यात्रा जारी रखें।'
                                          : 'Continue your JanSetu journey.')
                                      : (l10n.isHindi
                                          ? 'कल्याणकारी अवसरों को खोजने और प्रबंधित करने के लिए जनसेतु से जुड़ें।'
                                          : 'Join JanSetu to discover and manage welfare opportunities.'),
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                color: JanSetuTokens.textSecondary,
                                fontSize: 13,
                              ),
                            ),
                            const SizedBox(height: 24),

                            // Error
                            if (_errorMessage != null) ...[
                              _ErrorBanner(message: _errorMessage!),
                              const SizedBox(height: 16),
                            ],

                            // Email / phone field
                            _InputField(
                              controller: _identifierController,
                              hint: isForgot
                                  ? 'Email or Mobile Number'
                                  : isLogin
                                      ? 'Email or Mobile Number'
                                      : 'Email or Mobile Number',
                              prefixIcon: Icons.mail_outline_rounded,
                              keyboardType: TextInputType.emailAddress,
                            ),
                            const SizedBox(height: 12),

                            // Password
                            if (!isForgot) ...[
                              _InputField(
                                controller: _passwordController,
                                hint: 'Enter your password',
                                prefixIcon: Icons.lock_outline_rounded,
                                obscureText: _obscurePassword,
                                onToggle: () => setState(() => _obscurePassword = !_obscurePassword),
                              ),
                              const SizedBox(height: 12),
                            ],

                            // Confirm password (register)
                            if (isRegister) ...[
                              _InputField(
                                controller: _confirmPasswordController,
                                hint: 'Confirm your password',
                                prefixIcon: Icons.lock_outline_rounded,
                                obscureText: _obscureConfirm,
                                onToggle: () => setState(() => _obscureConfirm = !_obscureConfirm),
                              ),
                              const SizedBox(height: 12),
                            ],

                            // Remember me + Forgot (login only)
                            if (isLogin) ...[
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  GestureDetector(
                                    onTap: () => setState(() => _rememberMe = !_rememberMe),
                                    child: Row(
                                      children: [
                                        _GoldCheckbox(checked: _rememberMe),
                                        const SizedBox(width: 8),
                                        const Text(
                                          'Remember me',
                                          style: TextStyle(
                                            color: JanSetuTokens.textSecondary,
                                            fontSize: 13,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  GestureDetector(
                                    onTap: () => _switchMode(_AuthMode.forgotPassword),
                                    child: const Text(
                                      'Forgot Password?',
                                      style: TextStyle(
                                        color: JanSetuTokens.goldPrimary,
                                        fontSize: 13,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 20),
                            ] else
                              const SizedBox(height: 20),

                            // CTA Button
                            _GoldButton(
                              label: isForgot
                                  ? (l10n.isHindi ? 'जारी रखें' : 'Continue')
                                  : isLogin
                                      ? (l10n.isHindi ? 'लॉग इन करें' : 'Log In')
                                      : (l10n.isHindi ? 'खाता बनाएं' : 'Create Account'),
                              isLoading: _isLoading,
                              onTap: _handleSubmit,
                            ),
                            const SizedBox(height: 16),

                            // Switch link
                            Center(
                              child: RichText(
                                text: TextSpan(
                                  style: const TextStyle(
                                    color: JanSetuTokens.textSecondary,
                                    fontSize: 13,
                                  ),
                                  children: [
                                    TextSpan(
                                      text: isLogin
                                          ? (l10n.isHindi ? 'खाता नहीं है? ' : "Don't have an account? ")
                                          : isForgot
                                              ? (l10n.isHindi ? 'वापस ' : 'Back to ')
                                              : (l10n.isHindi ? 'क्या आपके पास पहले से खाता है? ' : 'Already have an account? '),
                                    ),
                                    WidgetSpan(
                                      child: GestureDetector(
                                        onTap: () => _switchMode(
                                          isLogin ? _AuthMode.register : _AuthMode.login,
                                        ),
                                        child: Text(
                                          isLogin
                                              ? (l10n.isHindi ? 'खाता बनाएं' : 'Create an account')
                                              : (l10n.isHindi ? 'लॉग इन करें' : 'Log in'),
                                          style: const TextStyle(
                                            color: JanSetuTokens.goldPrimary,
                                            fontSize: 13,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Atmospheric Background ───────────────────────────────────────────────────
// Recreates the JanSetu web: dark navy + amber glow + golden wave lines
// + Indian silhouette monuments
class _AtmosphericBackground extends StatelessWidget {
  const _AtmosphericBackground();

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return Stack(
      fit: StackFit.expand,
      children: [
        // Base gradient
        Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Color(0xFF060A12),
                Color(0xFF0A1020),
                Color(0xFF111826),
                Color(0xFF0D0F18),
              ],
              stops: [0.0, 0.4, 0.7, 1.0],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),

        // Warm amber glow right side (matching the web screenshot)
        Positioned(
          right: -size.width * 0.2,
          top: size.height * 0.15,
          child: Container(
            width: size.width * 0.8,
            height: size.height * 0.5,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  const Color(0xFFD4860A).withOpacity(0.35),
                  const Color(0xFFB8650A).withOpacity(0.15),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),

        // Subtle moon glow top-left
        Positioned(
          left: size.width * 0.05,
          top: size.height * 0.05,
          child: Container(
            width: size.width * 0.4,
            height: size.height * 0.25,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  Colors.white.withOpacity(0.06),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),

        // Golden wave lines + Indian silhouettes via CustomPaint
        CustomPaint(
          size: Size(size.width, size.height),
          painter: _ScenePainter(),
        ),
      ],
    );
  }
}

class _ScenePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    _drawGoldenWaves(canvas, size);
    _drawSilhouettes(canvas, size);
  }

  void _drawGoldenWaves(Canvas canvas, Size size) {
    final wavePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2
      ..strokeCap = StrokeCap.round;

    // Wave 1 — main bright wave
    wavePaint.shader = LinearGradient(
      colors: [
        Colors.transparent,
        const Color(0xFFF5C77C).withOpacity(0.08),
        const Color(0xFFF5C77C).withOpacity(0.7),
        const Color(0xFFF5C77C).withOpacity(0.8),
        const Color(0xFFF5C77C).withOpacity(0.4),
        const Color(0xFFF5C77C).withOpacity(0.08),
        Colors.transparent,
      ],
      stops: const [0.0, 0.1, 0.35, 0.55, 0.75, 0.9, 1.0],
    ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    final path1 = Path();
    path1.moveTo(0, size.height * 0.47);
    path1.cubicTo(
      size.width * 0.15, size.height * 0.38,
      size.width * 0.30, size.height * 0.52,
      size.width * 0.50, size.height * 0.44,
    );
    path1.cubicTo(
      size.width * 0.68, size.height * 0.37,
      size.width * 0.82, size.height * 0.50,
      size.width, size.height * 0.43,
    );
    canvas.drawPath(path1, wavePaint);

    // Wave 2 — slightly below, dimmer
    final wavePaint2 = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.8;
    wavePaint2.shader = LinearGradient(
      colors: [
        Colors.transparent,
        const Color(0xFFF5C77C).withOpacity(0.03),
        const Color(0xFFF5C77C).withOpacity(0.25),
        const Color(0xFFF5C77C).withOpacity(0.3),
        const Color(0xFFF5C77C).withOpacity(0.12),
        Colors.transparent,
      ],
      stops: const [0.0, 0.1, 0.35, 0.6, 0.85, 1.0],
    ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    final path2 = Path();
    path2.moveTo(0, size.height * 0.52);
    path2.cubicTo(
      size.width * 0.20, size.height * 0.45,
      size.width * 0.40, size.height * 0.56,
      size.width * 0.60, size.height * 0.48,
    );
    path2.cubicTo(
      size.width * 0.78, size.height * 0.41,
      size.width * 0.90, size.height * 0.54,
      size.width, size.height * 0.49,
    );
    canvas.drawPath(path2, wavePaint2);

    // Glowing dots on wave
    final dotPaint = Paint()
      ..color = const Color(0xFFF5C77C).withOpacity(0.9)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3);
    _drawWaveDot(canvas, size, 0.20, 0.445, dotPaint, 3);
    _drawWaveDot(canvas, size, 0.50, 0.44, dotPaint, 4);
    _drawWaveDot(canvas, size, 0.82, 0.46, dotPaint, 2.5);
  }

  void _drawWaveDot(Canvas canvas, Size size, double xFrac, double yFrac,
      Paint paint, double radius) {
    canvas.drawCircle(
      Offset(size.width * xFrac, size.height * yFrac),
      radius,
      paint,
    );
  }

  void _drawSilhouettes(Canvas canvas, Size size) {
    final silPaint = Paint()
      ..color = const Color(0xFF1A2234).withOpacity(0.8)
      ..style = PaintingStyle.fill;

    // Right side — large temple/mosque silhouettes
    _drawTemple(canvas, size, size.width * 0.72, size.height * 0.55, 90, silPaint);
    _drawTemple(canvas, size, size.width * 0.82, size.height * 0.58, 70, silPaint);
    _drawTemple(canvas, size, size.width * 0.91, size.height * 0.60, 55, silPaint);

    // Left side — smaller silhouettes
    _drawSmallHouse(canvas, size, size.width * 0.04, size.height * 0.72, silPaint);
    _drawSmallHouse(canvas, size, size.width * 0.10, size.height * 0.75, silPaint);
  }

  void _drawTemple(Canvas canvas, Size size, double x, double baseY,
      double height, Paint paint) {
    final w = height * 0.45;
    final path = Path();

    // Base
    path.addRect(Rect.fromLTWH(x - w / 2, baseY - height * 0.25, w, height * 0.25));

    // Middle tier
    path.addRect(Rect.fromLTWH(x - w * 0.35, baseY - height * 0.55, w * 0.7, height * 0.3));

    // Spire
    path.moveTo(x, baseY - height);
    path.lineTo(x - w * 0.18, baseY - height * 0.55);
    path.lineTo(x + w * 0.18, baseY - height * 0.55);
    path.close();

    // Top finial
    path.addOval(Rect.fromCenter(
      center: Offset(x, baseY - height),
      width: w * 0.10,
      height: w * 0.15,
    ));

    canvas.drawPath(path, paint);
  }

  void _drawSmallHouse(Canvas canvas, Size size, double x, double baseY, Paint paint) {
    final path = Path();
    path.addRect(Rect.fromLTWH(x, baseY - 40, 30, 40));
    path.moveTo(x - 5, baseY - 40);
    path.lineTo(x + 15, baseY - 65);
    path.lineTo(x + 35, baseY - 40);
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// ─── Auth Card ────────────────────────────────────────────────────────────────
class _AuthCard extends StatelessWidget {
  final Widget child;
  const _AuthCard({required this.child});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          padding: const EdgeInsets.all(28),
          decoration: BoxDecoration(
            color: const Color(0xFF0D1527).withOpacity(0.88),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.white.withOpacity(0.07),
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x80000000),
                offset: Offset(0, 20),
                blurRadius: 48,
                spreadRadius: -8,
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}

// ─── JanSetu Logo ─────────────────────────────────────────────────────────────
class _JanSetuLogo extends StatelessWidget {
  const _JanSetuLogo();

  @override
  Widget build(BuildContext context) {
    return const JanSetuBrand(
      variant: JanSetuBrandVariant.full,
      size: JanSetuBrandSize.lg,
      showTagline: true,
    );
  }
}

// ─── Input Field ──────────────────────────────────────────────────────────────
class _InputField extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final IconData prefixIcon;
  final bool obscureText;
  final VoidCallback? onToggle;
  final TextInputType? keyboardType;

  const _InputField({
    required this.controller,
    required this.hint,
    required this.prefixIcon,
    this.obscureText = false,
    this.onToggle,
    this.keyboardType,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 50,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.09)),
      ),
      child: TextField(
        controller: controller,
        obscureText: obscureText,
        keyboardType: keyboardType,
        style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: TextStyle(color: JanSetuTokens.textMuted, fontSize: 14),
          prefixIcon: Icon(prefixIcon, color: JanSetuTokens.textMuted, size: 18),
          suffixIcon: onToggle != null
              ? IconButton(
                  icon: Icon(
                    obscureText ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                    color: JanSetuTokens.textMuted,
                    size: 18,
                  ),
                  onPressed: onToggle,
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 15),
        ),
      ),
    );
  }
}

// ─── Gold CTA Button ──────────────────────────────────────────────────────────
class _GoldButton extends StatelessWidget {
  final String label;
  final bool isLoading;
  final VoidCallback onTap;

  const _GoldButton({required this.label, required this.isLoading, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isLoading ? null : onTap,
      child: Container(
        height: 50,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFFCE7A9), Color(0xFFF5C77C), Color(0xFFE5A952)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: JanSetuTokens.goldPrimary.withOpacity(0.30),
              offset: const Offset(0, 6),
              blurRadius: 18,
            ),
          ],
        ),
        child: Center(
          child: isLoading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Color(0xFF140E05),
                  ),
                )
              : Text(
                  label,
                  style: const TextStyle(
                    color: Color(0xFF140E05),
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.3,
                  ),
                ),
        ),
      ),
    );
  }
}

// ─── Gold Checkbox ────────────────────────────────────────────────────────────
class _GoldCheckbox extends StatelessWidget {
  final bool checked;
  const _GoldCheckbox({required this.checked});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 16,
      height: 16,
      decoration: BoxDecoration(
        color: checked ? JanSetuTokens.goldPrimary : Colors.transparent,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: checked ? JanSetuTokens.goldPrimary : JanSetuTokens.textMuted,
          width: 1.5,
        ),
      ),
      child: checked
          ? const Icon(Icons.check, size: 11, color: Color(0xFF140E05))
          : null,
    );
  }
}

// ─── Error Banner ─────────────────────────────────────────────────────────────
class _ErrorBanner extends StatelessWidget {
  final String message;
  const _ErrorBanner({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: JanSetuTokens.rosePrimary.withOpacity(0.12),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: JanSetuTokens.rosePrimary.withOpacity(0.35)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, color: JanSetuTokens.rosePrimary, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(message,
                style: const TextStyle(color: JanSetuTokens.rosePrimary, fontSize: 13)),
          ),
        ],
      ),
    );
  }
}

// ─── Top Bar (language + icons) ───────────────────────────────────────────────
class _TopBar extends StatelessWidget {
  final bool isHindi;
  final VoidCallback onLanguageToggle;
  const _TopBar({required this.isHindi, required this.onLanguageToggle});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _TopBarChip(
          child: const Icon(Icons.settings_outlined, color: JanSetuTokens.goldPrimary, size: 15),
          onTap: () {},
        ),
        const SizedBox(width: 8),
        _TopBarChip(
          child: Text(
            isHindi ? 'HI' : 'EN',
            style: const TextStyle(
              color: JanSetuTokens.goldPrimary,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          onTap: onLanguageToggle,
        ),
        const SizedBox(width: 8),
        _TopBarChip(
          child: const Icon(Icons.notifications_outlined, color: JanSetuTokens.goldPrimary, size: 15),
          onTap: () {},
        ),
      ],
    );
  }
}

class _TopBarChip extends StatelessWidget {
  final Widget child;
  final VoidCallback onTap;
  const _TopBarChip({required this.child, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.06),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white.withOpacity(0.10)),
        ),
        child: child,
      ),
    );
  }
}
