import 'package:flutter/material.dart';
import '../core/localization/app_localizations.dart';
import '../core/models/models.dart';
import '../core/repositories/auth_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';
import '../shared/widgets/gold_button.dart';

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

class _AuthScreenState extends State<AuthScreen> with SingleTickerProviderStateMixin {
  bool _isLogin = true;
  bool _isLoading = false;
  String? _errorMessage;

  final _identifierController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _fadeAnim = CurvedAnimation(parent: _animController, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.08),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic));

    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    _identifierController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    final l10n = context.l10n;
    setState(() {
      _errorMessage = null;
    });

    final identifier = _identifierController.text.trim();
    final password = _passwordController.text;

    if (identifier.isEmpty || password.isEmpty) {
      setState(() {
        _errorMessage = l10n.text('auth.errorRequired');
      });
      return;
    }

    if (password.length < 8) {
      setState(() {
        _errorMessage = l10n.text('auth.errorShortPass');
      });
      return;
    }

    if (!_isLogin) {
      final confirmPassword = _confirmPasswordController.text;
      if (password != confirmPassword) {
        setState(() {
          _errorMessage = l10n.text('auth.errorMismatch');
        });
        return;
      }
    }

    setState(() {
      _isLoading = true;
    });

    try {
      if (_isLogin) {
        await widget.authRepository.login(
          username: identifier,
          password: password,
        );
      } else {
        final isEmail = identifier.contains('@');
        final email = isEmail ? identifier : null;
        final phone = !isEmail ? identifier : (_phoneController.text.trim().isNotEmpty ? _phoneController.text.trim() : null);

        await widget.authRepository.register(
          email: email,
          phone: phone,
          password: password,
          preferredLanguage: l10n.currentLanguageCode,
        );
      }

      widget.onAuthenticated();
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('ApiException: ', '').replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return CinematicScaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: FadeTransition(
            opacity: _fadeAnim,
            child: SlideTransition(
              position: _slideAnim,
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 440),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Top Bar with Language Toggle
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Sovereign Emblem / Monogram
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: JanSetuTokens.goldPrimary.withOpacity(0.12),
                                border: Border.all(color: JanSetuTokens.goldPrimary.withOpacity(0.3)),
                              ),
                              child: const Icon(
                                Icons.account_balance_rounded,
                                color: JanSetuTokens.goldPrimary,
                                size: 20,
                              ),
                            ),
                            const SizedBox(width: 10),
                            const Text(
                              'JANSETU',
                              style: TextStyle(
                                color: JanSetuTokens.textPrimary,
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 1.5,
                              ),
                            ),
                          ],
                        ),

                        // Language Toggle Chip
                        InkWell(
                          onTap: widget.onLanguageToggle,
                          borderRadius: BorderRadius.circular(20),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: JanSetuTokens.bgGlassSecondary,
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(color: JanSetuTokens.glassBorderFocus.withOpacity(0.4)),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.language_rounded, color: JanSetuTokens.goldPrimary, size: 16),
                                const SizedBox(width: 6),
                                Text(
                                  l10n.isHindi ? 'English' : 'हिंदी',
                                  style: const TextStyle(
                                    color: JanSetuTokens.goldPrimary,
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 28),

                    // Main Glass Authentication Card
                    GlassCard(
                      padding: const EdgeInsets.all(28),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Card Header
                          Text(
                            _isLogin ? l10n.text('auth.welcomeBack') : l10n.text('auth.register'),
                            style: const TextStyle(
                              color: JanSetuTokens.textPrimary,
                              fontSize: 24,
                              fontWeight: FontWeight.w700,
                              letterSpacing: -0.3,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _isLogin ? l10n.text('auth.loginDesc') : l10n.text('auth.registerDesc'),
                            style: const TextStyle(
                              color: JanSetuTokens.textSecondary,
                              fontSize: 13,
                              height: 1.45,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 24),

                          // Tab Selector (Login vs Register)
                          Container(
                            padding: const EdgeInsets.all(4),
                            decoration: BoxDecoration(
                              color: JanSetuTokens.bgDeep.withOpacity(0.6),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: JanSetuTokens.glassBorderSubtle),
                            ),
                            child: Row(
                              children: [
                                Expanded(
                                  child: _AuthTabButton(
                                    label: l10n.text('auth.login'),
                                    isSelected: _isLogin,
                                    onTap: () {
                                      setState(() {
                                        _isLogin = true;
                                        _errorMessage = null;
                                      });
                                    },
                                  ),
                                ),
                                Expanded(
                                  child: _AuthTabButton(
                                    label: l10n.text('auth.register'),
                                    isSelected: !_isLogin,
                                    onTap: () {
                                      setState(() {
                                        _isLogin = false;
                                        _errorMessage = null;
                                      });
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 20),

                          // Error Banner
                          if (_errorMessage != null) ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: JanSetuTokens.rosePrimary.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: JanSetuTokens.rosePrimary.withOpacity(0.4)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.error_outline_rounded, color: JanSetuTokens.rosePrimary, size: 18),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _errorMessage!,
                                      style: const TextStyle(
                                        color: JanSetuTokens.rosePrimary,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],

                          // Email / Mobile Field
                          Text(
                            _isLogin
                                ? '${l10n.text('auth.emailLabel')} / ${l10n.text('auth.phoneLabel')}'
                                : l10n.text('auth.emailLabel'),
                            style: const TextStyle(
                              color: JanSetuTokens.textSecondary,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _identifierController,
                            style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 15),
                            decoration: InputDecoration(
                              hintText: _isLogin ? 'citizen@example.gov.in / 9876543210' : 'citizen@example.gov.in',
                              prefixIcon: const Icon(Icons.person_outline_rounded, color: JanSetuTokens.goldPrimary, size: 20),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Password Field
                          Text(
                            l10n.text('auth.passwordLabel'),
                            style: const TextStyle(
                              color: JanSetuTokens.textSecondary,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _passwordController,
                            obscureText: true,
                            style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 15),
                            decoration: InputDecoration(
                              hintText: l10n.text('auth.passwordPlaceholder'),
                              prefixIcon: const Icon(Icons.lock_outline_rounded, color: JanSetuTokens.goldPrimary, size: 20),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Confirm Password (Only in Register mode)
                          if (!_isLogin) ...[
                            Text(
                              l10n.text('auth.confirmPasswordLabel'),
                              style: const TextStyle(
                                color: JanSetuTokens.textSecondary,
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            const SizedBox(height: 6),
                            TextField(
                              controller: _confirmPasswordController,
                              obscureText: true,
                              style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 15),
                              decoration: InputDecoration(
                                hintText: l10n.text('auth.confirmPasswordPlaceholder'),
                                prefixIcon: const Icon(Icons.lock_reset_rounded, color: JanSetuTokens.goldPrimary, size: 20),
                              ),
                            ),
                            const SizedBox(height: 20),
                          ],

                          // CTA Button
                          GoldButton(
                            text: _isLogin ? l10n.text('auth.loginBtn') : l10n.text('auth.registerBtn'),
                            isLoading: _isLoading,
                            icon: Icons.arrow_forward_rounded,
                            onPressed: _handleSubmit,
                          ),
                          const SizedBox(height: 16),

                          // Sovereign Privacy Charter Notice
                          Text(
                            l10n.text('auth.termsConsent'),
                            style: const TextStyle(
                              color: JanSetuTokens.textMuted,
                              fontSize: 11,
                              height: 1.35,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _AuthTabButton extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _AuthTabButton({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? JanSetuTokens.bgSurface : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
          border: isSelected ? Border.all(color: JanSetuTokens.glassBorderFocus.withOpacity(0.5)) : null,
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? JanSetuTokens.goldPrimary : JanSetuTokens.textSecondary,
              fontSize: 14,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            ),
          ),
        ),
      ),
    );
  }
}
