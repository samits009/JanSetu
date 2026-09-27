import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/localization/app_localizations.dart';
import '../core/models/models.dart';
import '../core/repositories/citizen_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';
import '../shared/widgets/gold_button.dart';
import '../shared/widgets/jansetu_brand.dart';

class HomeScreen extends StatefulWidget {
  final CitizenRepository citizenRepository;
  final Function(int) onNavigateTab;
  final VoidCallback onSelectScheme;

  const HomeScreen({
    super.key,
    required this.citizenRepository,
    required this.onNavigateTab,
    required this.onSelectScheme,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  WelfareStateModel? _welfareState;
  Map<String, dynamic>? _citizenProfile;

  final _currencyFormatter = NumberFormat.currency(
    locale: 'en_IN',
    symbol: '₹',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _fetchWelfareData();
  }

  Future<void> _fetchWelfareData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final results = await Future.wait([
        widget.citizenRepository.getWelfareState(),
        widget.citizenRepository.getMyProfile(),
      ]);

      if (mounted) {
        setState(() {
          _welfareState = results[0] as WelfareStateModel;
          _citizenProfile = results[1] as Map<String, dynamic>;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('ApiException: ', '');
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final citizenName = _citizenProfile?['name']?.toString() ?? 'Citizen';

    return CinematicScaffold(
      body: RefreshIndicator(
        onRefresh: _fetchWelfareData,
        color: JanSetuTokens.goldPrimary,
        backgroundColor: JanSetuTokens.bgSurface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Top Bar: Citizen Status & Greeting
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: JanSetuTokens.emeraldPrimary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: JanSetuTokens.emeraldPrimary.withOpacity(0.4)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.verified_user_rounded, color: JanSetuTokens.emeraldPrimary, size: 14),
                            const SizedBox(width: 4),
                            Text(
                              l10n.text('dashboard.sovereignBadge').toUpperCase(),
                              style: const TextStyle(
                                color: JanSetuTokens.emeraldPrimary,
                                fontSize: 10,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.8,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${l10n.text('dashboard.welcome')}, $citizenName',
                        style: const TextStyle(
                          color: JanSetuTokens.textPrimary,
                          fontSize: 22,
                          fontWeight: FontWeight.w700,
                          letterSpacing: -0.3,
                        ),
                      ),
                    ],
                  ),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.refresh_rounded, color: JanSetuTokens.goldPrimary),
                        onPressed: _fetchWelfareData,
                        tooltip: 'Refresh',
                      ),
                      const SizedBox(width: 4),
                      const JanSetuBrand(
                        variant: JanSetuBrandVariant.icon,
                        size: JanSetuBrandSize.sm,
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 20),

              if (_isLoading) ...[
                const SizedBox(height: 60),
                const Center(
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(JanSetuTokens.goldPrimary),
                  ),
                ),
              ] else if (_errorMessage != null) ...[
                GlassCard(
                  child: Column(
                    children: [
                      const Icon(Icons.wifi_off_rounded, color: JanSetuTokens.amberPrimary, size: 40),
                      const SizedBox(height: 12),
                      Text(
                        _errorMessage!,
                        style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      GoldButton(
                        text: l10n.text('common.retry'),
                        onPressed: _fetchWelfareData,
                        height: 44,
                        fullWidth: false,
                      ),
                    ],
                  ),
                ),
              ] else if (_welfareState != null) ...[
                // Main Welfare Entitlement Card
                GlassCard(
                  padding: const EdgeInsets.all(24),
                  borderColor: JanSetuTokens.glassBorderFocus.withOpacity(0.5),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            l10n.text('dashboard.protectedMonthly'),
                            style: const TextStyle(
                              color: JanSetuTokens.textSecondary,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const Icon(Icons.shield_outlined, color: JanSetuTokens.goldPrimary, size: 20),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        _currencyFormatter.format(_welfareState!.totalPotentialMonthlyBenefit),
                        style: const TextStyle(
                          color: JanSetuTokens.goldPrimary,
                          fontSize: 34,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.5,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Direct monthly entitlement derived strictly from official central & state policy rules.',
                        style: TextStyle(
                          color: JanSetuTokens.textMuted.withOpacity(0.9),
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 18),
                      const Divider(color: JanSetuTokens.glassBorder, height: 1),
                      const SizedBox(height: 16),

                      // Metrics Grid
                      Row(
                        children: [
                          Expanded(
                            child: _MetricItem(
                              label: l10n.text('dashboard.activeSchemes'),
                              value: '${_welfareState!.eligibleSchemesCount}',
                              icon: Icons.assignment_turned_in_outlined,
                              color: JanSetuTokens.skyPrimary,
                            ),
                          ),
                          Container(width: 1, height: 36, color: JanSetuTokens.glassBorder),
                          Expanded(
                            child: _MetricItem(
                              label: l10n.text('dashboard.readinessScore'),
                              value: '${(_welfareState!.evidenceReadinessScore * 100).toInt()}%',
                              icon: Icons.checklist_rounded,
                              color: JanSetuTokens.emeraldPrimary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Quick Action Banner (Evidence Vault & Agent)
                Row(
                  children: [
                    Expanded(
                      child: _QuickActionButton(
                        icon: Icons.document_scanner_outlined,
                        title: l10n.text('nav.documents'),
                        subtitle: 'Upload IDs & Proofs',
                        onTap: () => widget.onNavigateTab(2),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _QuickActionButton(
                        icon: Icons.smart_toy_outlined,
                        title: l10n.text('nav.agent'),
                        subtitle: 'Ask Sovereign AI',
                        onTap: () => widget.onNavigateTab(4),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Actions Requiring Attention
                if (_welfareState!.recommendedActions.isNotEmpty) ...[
                  Row(
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: JanSetuTokens.amberPrimary, size: 18),
                      const SizedBox(width: 8),
                      Text(
                        l10n.text('dashboard.actionNeeded'),
                        style: const TextStyle(
                          color: JanSetuTokens.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  for (final action in _welfareState!.recommendedActions) ...[
                    Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: JanSetuTokens.amberPrimary.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: JanSetuTokens.amberPrimary.withOpacity(0.25)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.arrow_right_rounded, color: JanSetuTokens.amberPrimary, size: 22),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              action,
                              style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 20),
                ],

                // Active Benefits Preview Section
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.text('dashboard.activeSchemes'),
                      style: const TextStyle(
                        color: JanSetuTokens.textPrimary,
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    TextButton(
                      onPressed: () => widget.onNavigateTab(1),
                      child: Text(
                        l10n.text('dashboard.exploreAll'),
                        style: const TextStyle(color: JanSetuTokens.goldPrimary, fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),

                if (_welfareState!.activeSchemes.isEmpty)
                  GlassCard(
                    padding: const EdgeInsets.all(20),
                    child: Center(
                      child: Text(
                        'Complete your onboarding details to unlock statutory benefits.',
                        style: TextStyle(color: JanSetuTokens.textMuted.withOpacity(0.9), fontSize: 13),
                      ),
                    ),
                  )
                else
                  for (final scheme in _welfareState!.activeSchemes.take(3)) ...[
                    Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: GlassCard(
                        padding: const EdgeInsets.all(18),
                        onTap: () => widget.onNavigateTab(1),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    scheme.localizedName(l10n.currentLanguageCode),
                                    style: const TextStyle(
                                      color: JanSetuTokens.textPrimary,
                                      fontSize: 16,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                                if (scheme.monthlyValue != null && scheme.monthlyValue! > 0)
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: JanSetuTokens.goldPrimary.withOpacity(0.15),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      _currencyFormatter.format(scheme.monthlyValue),
                                      style: const TextStyle(
                                        color: JanSetuTokens.goldPrimary,
                                        fontSize: 12,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                            if (scheme.ministry != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                scheme.ministry!,
                                style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12),
                              ),
                            ],
                            const SizedBox(height: 10),
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: JanSetuTokens.emeraldPrimary.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    scheme.status.toUpperCase(),
                                    style: const TextStyle(
                                      color: JanSetuTokens.emeraldPrimary,
                                      fontSize: 10,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                                const Spacer(),
                                const Text(
                                  'View Details →',
                                  style: TextStyle(
                                    color: JanSetuTokens.goldPrimary,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                const SizedBox(height: 24),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _MetricItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _MetricItem({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 6),
            Text(
              value,
              style: TextStyle(
                color: color,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            color: JanSetuTokens.textSecondary,
            fontSize: 12,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _QuickActionButton({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: JanSetuTokens.goldPrimary, size: 24),
          const SizedBox(height: 10),
          Text(
            title,
            style: const TextStyle(
              color: JanSetuTokens.textPrimary,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: const TextStyle(
              color: JanSetuTokens.textMuted,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
}
