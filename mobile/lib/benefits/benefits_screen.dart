import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/localization/app_localizations.dart';
import '../core/models/models.dart';
import '../core/repositories/citizen_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';
import '../shared/widgets/gold_button.dart';

class BenefitsScreen extends StatefulWidget {
  final CitizenRepository citizenRepository;
  final Function(String schemeId)? onPrepareApplication;

  const BenefitsScreen({
    super.key,
    required this.citizenRepository,
    this.onPrepareApplication,
  });

  @override
  State<BenefitsScreen> createState() => _BenefitsScreenState();
}

class _BenefitsScreenState extends State<BenefitsScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<SchemeBenefitModel> _schemes = [];
  SchemeBenefitModel? _selectedScheme;
  Map<String, dynamic>? _whyApplyDetails;
  bool _isLoadingWhyApply = false;

  final _currencyFormatter = NumberFormat.currency(
    locale: 'en_IN',
    symbol: '₹',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _fetchBenefits();
  }

  Future<void> _fetchBenefits() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final state = await widget.citizenRepository.getWelfareState();
      if (mounted) {
        setState(() {
          _schemes = state.activeSchemes;
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

  Future<void> _showSchemeDetails(SchemeBenefitModel scheme) async {
    setState(() {
      _selectedScheme = scheme;
      _whyApplyDetails = null;
      _isLoadingWhyApply = true;
    });

    try {
      final details = await widget.citizenRepository.getBenefitWhyApply(scheme.id);
      if (mounted) {
        setState(() {
          _whyApplyDetails = details;
          _isLoadingWhyApply = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _isLoadingWhyApply = false;
        });
      }
    }

    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _SchemeDetailSheet(
        scheme: scheme,
        details: _whyApplyDetails,
        isLoadingDetails: _isLoadingWhyApply,
        onPrepare: () {
          Navigator.pop(ctx);
          if (widget.onPrepareApplication != null) {
            widget.onPrepareApplication!(scheme.id);
          }
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return CinematicScaffold(
      body: RefreshIndicator(
        onRefresh: _fetchBenefits,
        color: JanSetuTokens.goldPrimary,
        backgroundColor: JanSetuTokens.bgSurface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Text(
                l10n.text('benefits.title'),
                style: const TextStyle(
                  color: JanSetuTokens.textPrimary,
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                l10n.text('benefits.subtitle'),
                style: const TextStyle(
                  color: JanSetuTokens.textSecondary,
                  fontSize: 13,
                  height: 1.45,
                ),
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
                      const Icon(Icons.error_outline_rounded, color: JanSetuTokens.rosePrimary, size: 36),
                      const SizedBox(height: 12),
                      Text(
                        _errorMessage!,
                        style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      GoldButton(
                        text: l10n.text('common.retry'),
                        onPressed: _fetchBenefits,
                        height: 44,
                        fullWidth: false,
                      ),
                    ],
                  ),
                ),
              ] else if (_schemes.isEmpty) ...[
                GlassCard(
                  padding: const EdgeInsets.all(28),
                  child: Column(
                    children: [
                      const Icon(Icons.assignment_outlined, color: JanSetuTokens.goldPrimary, size: 44),
                      const SizedBox(height: 16),
                      const Text(
                        'No Eligible Schemes Evaluated Yet',
                        style: TextStyle(color: JanSetuTokens.textPrimary, fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Update your profile and location to let JanSetu match official welfare criteria.',
                        style: TextStyle(color: JanSetuTokens.textMuted, fontSize: 13),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ] else ...[
                for (final scheme in _schemes) ...[
                  Container(
                    margin: const EdgeInsets.only(bottom: 14),
                    child: GlassCard(
                      padding: const EdgeInsets.all(20),
                      onTap: () => _showSchemeDetails(scheme),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      scheme.localizedName(l10n.currentLanguageCode),
                                      style: const TextStyle(
                                        color: JanSetuTokens.textPrimary,
                                        fontSize: 17,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                    if (scheme.ministry != null) ...[
                                      const SizedBox(height: 4),
                                      Text(
                                        scheme.ministry!,
                                        style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                              if (scheme.monthlyValue != null && scheme.monthlyValue! > 0)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                                  decoration: BoxDecoration(
                                    color: JanSetuTokens.goldPrimary.withOpacity(0.15),
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: JanSetuTokens.goldPrimary.withOpacity(0.3)),
                                  ),
                                  child: Text(
                                    _currencyFormatter.format(scheme.monthlyValue),
                                    style: const TextStyle(
                                      color: JanSetuTokens.goldPrimary,
                                      fontSize: 13,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 12),

                          // Description
                          Text(
                            scheme.localizedDescription(l10n.currentLanguageCode),
                            style: const TextStyle(
                              color: JanSetuTokens.textSecondary,
                              fontSize: 13,
                              height: 1.4,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 16),

                          // Footer Chips
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: JanSetuTokens.emeraldPrimary.withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.check_circle_outline_rounded, color: JanSetuTokens.emeraldPrimary, size: 12),
                                    const SizedBox(width: 4),
                                    Text(
                                      scheme.status.toUpperCase(),
                                      style: const TextStyle(
                                        color: JanSetuTokens.emeraldPrimary,
                                        fontSize: 10,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 10),
                              Text(
                                'Readiness ${(scheme.readinessScore * 100).toInt()}%',
                                style: const TextStyle(color: JanSetuTokens.skyPrimary, fontSize: 12, fontWeight: FontWeight.w600),
                              ),
                              const Spacer(),
                              Text(
                                l10n.text('benefits.viewDetail'),
                                style: const TextStyle(
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
              ],
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class _SchemeDetailSheet extends StatelessWidget {
  final SchemeBenefitModel scheme;
  final Map<String, dynamic>? details;
  final bool isLoadingDetails;
  final VoidCallback onPrepare;

  const _SchemeDetailSheet({
    required this.scheme,
    this.details,
    required this.isLoadingDetails,
    required this.onPrepare,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return Container(
      height: MediaQuery.of(context).size.height * 0.82,
      decoration: BoxDecoration(
        color: JanSetuTokens.bgSurface.withOpacity(0.95),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        border: const Border(
          top: BorderSide(color: JanSetuTokens.goldPrimary, width: 1.5),
        ),
      ),
      child: Column(
        children: [
          // Drag handle
          const SizedBox(height: 12),
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: JanSetuTokens.glassBorder,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 16),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        scheme.localizedName(l10n.currentLanguageCode),
                        style: const TextStyle(
                          color: JanSetuTokens.textPrimary,
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      if (scheme.ministry != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          scheme.ministry!,
                          style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 13),
                        ),
                      ],
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close_rounded, color: JanSetuTokens.textMuted),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
          ),
          const Divider(color: JanSetuTokens.glassBorder, height: 20),

          // Scrollable detail contents
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Why This May Apply
                  Text(
                    l10n.text('benefits.whyApply'),
                    style: const TextStyle(
                      color: JanSetuTokens.goldPrimary,
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    scheme.localizedDescription(l10n.currentLanguageCode),
                    style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14, height: 1.5),
                  ),
                  const SizedBox(height: 20),

                  // Matched Statutory Criteria
                  if (scheme.matchReasons.isNotEmpty) ...[
                    Text(
                      l10n.text('benefits.matchedRules'),
                      style: const TextStyle(
                        color: JanSetuTokens.emeraldPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    for (final rule in scheme.matchReasons) ...[
                      Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.check_circle_rounded, color: JanSetuTokens.emeraldPrimary, size: 16),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                rule,
                                style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 16),
                  ],

                  // Pending / Unmet Rules
                  if (scheme.unmetRules.isNotEmpty) ...[
                    Text(
                      l10n.text('benefits.unmetRules'),
                      style: const TextStyle(
                        color: JanSetuTokens.amberPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    for (final rule in scheme.unmetRules) ...[
                      Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.info_outline_rounded, color: JanSetuTokens.amberPrimary, size: 16),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                rule,
                                style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 16),
                  ],

                  // Required Evidence Documents
                  if (scheme.requiredDocuments.isNotEmpty) ...[
                    Text(
                      l10n.text('benefits.requiredDocs'),
                      style: const TextStyle(
                        color: JanSetuTokens.skyPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    for (final doc in scheme.requiredDocuments) ...[
                      Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          children: [
                            const Icon(Icons.file_present_rounded, color: JanSetuTokens.skyPrimary, size: 16),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                doc,
                                style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 13),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 20),
                  ],

                  // Statutory Metadata
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: JanSetuTokens.bgDeep.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: JanSetuTokens.glassBorderSubtle),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Scheme Code: ${scheme.code}',
                          style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12),
                        ),
                        if (scheme.policyVersion != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            'Policy Gazette: ${scheme.policyVersion}',
                            style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12),
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Bottom Action
          Padding(
            padding: const EdgeInsets.all(20),
            child: GoldButton(
              text: l10n.text('benefits.applyNow'),
              icon: Icons.assignment_turned_in_rounded,
              onPressed: onPrepare,
            ),
          ),
        ],
      ),
    );
  }
}
