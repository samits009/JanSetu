import 'package:flutter/material.dart';
import '../core/localization/app_localizations.dart';
import '../core/models/models.dart';
import '../core/repositories/citizen_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';
import '../shared/widgets/gold_button.dart';

class ApplicationsScreen extends StatefulWidget {
  final CitizenRepository citizenRepository;

  const ApplicationsScreen({super.key, required this.citizenRepository});

  @override
  State<ApplicationsScreen> createState() => _ApplicationsScreenState();
}

class _ApplicationsScreenState extends State<ApplicationsScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<ApplicationItemModel> _applications = [];

  @override
  void initState() {
    super.initState();
    _fetchApplications();
  }

  Future<void> _fetchApplications() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final apps = await widget.citizenRepository.getApplications();
      if (mounted) {
        setState(() {
          _applications = apps;
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

  void _showConsentModal(ApplicationItemModel app) {
    final l10n = context.l10n;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _SovereignConsentSheet(
        app: app,
        citizenRepository: widget.citizenRepository,
        onConsentGranted: () {
          Navigator.pop(ctx);
          _fetchApplications();
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return CinematicScaffold(
      body: RefreshIndicator(
        onRefresh: _fetchApplications,
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
                l10n.text('applications.title'),
                style: const TextStyle(
                  color: JanSetuTokens.textPrimary,
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                l10n.text('applications.subtitle'),
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
                        onPressed: _fetchApplications,
                        height: 44,
                        fullWidth: false,
                      ),
                    ],
                  ),
                ),
              ] else if (_applications.isEmpty) ...[
                GlassCard(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    children: [
                      const Icon(Icons.post_add_rounded, color: JanSetuTokens.goldPrimary, size: 48),
                      const SizedBox(height: 16),
                      const Text(
                        'No Applications Prepared Yet',
                        style: TextStyle(color: JanSetuTokens.textPrimary, fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Explore your eligible schemes in the Benefits tab and select "Prepare Application" to initiate a verified claim.',
                        style: TextStyle(color: JanSetuTokens.textMuted, fontSize: 13),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ] else ...[
                for (final app in _applications) ...[
                  Container(
                    margin: const EdgeInsets.only(bottom: 14),
                    child: GlassCard(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  app.schemeName,
                                  style: const TextStyle(
                                    color: JanSetuTokens.textPrimary,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: _getStatusColor(app.status).withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  app.status.toUpperCase(),
                                  style: TextStyle(
                                    color: _getStatusColor(app.status),
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Applied: ${app.appliedAt?.split('T').first ?? 'Recent'}',
                            style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12),
                          ),
                          const SizedBox(height: 16),

                          // Real Timeline Stepper
                          _ApplicationTimeline(status: app.status),
                          const SizedBox(height: 16),

                          // Action Button if Consent or Review needed
                          if (app.status == 'prepared' || app.status == 'ready_for_consent') ...[
                            GoldButton(
                              text: l10n.text('consent.grant'),
                              icon: Icons.fingerprint_rounded,
                              height: 42,
                              onPressed: () => _showConsentModal(app),
                            ),
                          ] else if (app.status == 'submitted' || app.status == 'handed_off') ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: JanSetuTokens.skyPrimary.withOpacity(0.08),
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: JanSetuTokens.skyPrimary.withOpacity(0.25)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.open_in_new_rounded, color: JanSetuTokens.skyPrimary, size: 16),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      l10n.text('common.officialHandoff'),
                                      style: const TextStyle(color: JanSetuTokens.skyPrimary, fontSize: 12, fontWeight: FontWeight.w600),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
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

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'submitted':
      case 'handed_off':
      case 'approved':
        return JanSetuTokens.emeraldPrimary;
      case 'ready_for_consent':
      case 'prepared':
        return JanSetuTokens.goldPrimary;
      case 'needs_review':
        return JanSetuTokens.amberPrimary;
      default:
        return JanSetuTokens.skyPrimary;
    }
  }
}

class _ApplicationTimeline extends StatelessWidget {
  final String status;

  const _ApplicationTimeline({required this.status});

  @override
  Widget build(BuildContext context) {
    final stages = [
      'Prepared',
      'Reviewed',
      'Consent',
      'Submitted',
      'Decision',
    ];

    int currentStageIndex = 0;
    final s = status.toLowerCase();
    if (s == 'prepared') currentStageIndex = 0;
    if (s == 'reviewed') currentStageIndex = 1;
    if (s == 'consent_granted' || s == 'ready_for_consent') currentStageIndex = 2;
    if (s == 'submitted' || s == 'handed_off') currentStageIndex = 3;
    if (s == 'approved' || s == 'granted') currentStageIndex = 4;

    return Row(
      children: [
        for (int i = 0; i < stages.length; i++) ...[
          Expanded(
            child: Column(
              children: [
                Container(
                  width: 18,
                  height: 18,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: i <= currentStageIndex ? JanSetuTokens.goldPrimary : JanSetuTokens.bgDeep,
                    border: Border.all(
                      color: i <= currentStageIndex ? JanSetuTokens.goldPrimary : JanSetuTokens.glassBorder,
                      width: 2,
                    ),
                  ),
                  child: i < currentStageIndex
                      ? const Icon(Icons.check, size: 11, color: JanSetuTokens.goldTextOnBtn)
                      : null,
                ),
                const SizedBox(height: 4),
                Text(
                  stages[i],
                  style: TextStyle(
                    color: i <= currentStageIndex ? JanSetuTokens.textPrimary : JanSetuTokens.textMuted,
                    fontSize: 10,
                    fontWeight: i == currentStageIndex ? FontWeight.w700 : FontWeight.w400,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
          if (i < stages.length - 1)
            Expanded(
              child: Container(
                height: 2,
                color: i < currentStageIndex ? JanSetuTokens.goldPrimary : JanSetuTokens.glassBorderSubtle,
                margin: const EdgeInsets.only(bottom: 16),
              ),
            ),
        ],
      ],
    );
  }
}

class _SovereignConsentSheet extends StatefulWidget {
  final ApplicationItemModel app;
  final CitizenRepository citizenRepository;
  final VoidCallback onConsentGranted;

  const _SovereignConsentSheet({
    required this.app,
    required this.citizenRepository,
    required this.onConsentGranted,
  });

  @override
  State<_SovereignConsentSheet> createState() => _SovereignConsentSheetState();
}

class _SovereignConsentSheetState extends State<_SovereignConsentSheet> {
  bool _isProcessing = false;
  String? _errorMessage;

  Future<void> _handleGrantConsent() async {
    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      // Sovereign Consent protocol strictly uses backend
      await widget.citizenRepository.grantConsent(
        consentId: widget.app.id,
        action: 'GRANT',
        scope: 'APPLICATION_SUBMISSION',
      );
      widget.onConsentGranted();
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('ApiException: ', '');
        _isProcessing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return Container(
      height: MediaQuery.of(context).size.height * 0.72,
      decoration: BoxDecoration(
        color: JanSetuTokens.bgSurface.withOpacity(0.96),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        border: const Border(top: BorderSide(color: JanSetuTokens.goldPrimary, width: 2)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: JanSetuTokens.glassBorder,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Title
          Text(
            l10n.text('consent.readyToContinue'),
            style: const TextStyle(
              color: JanSetuTokens.textPrimary,
              fontSize: 22,
              fontWeight: FontWeight.w700,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6),
          Text(
            l10n.text('consent.youAreInControl'),
            style: const TextStyle(
              color: JanSetuTokens.textSecondary,
              fontSize: 13,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),

          // Consent Scope Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: JanSetuTokens.bgDeep.withOpacity(0.6),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: JanSetuTokens.glassBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _ConsentDetailRow(label: 'Scheme', value: widget.app.schemeName),
                const SizedBox(height: 10),
                _ConsentDetailRow(label: 'Action', value: 'Prepare & Official Handoff'),
                const SizedBox(height: 10),
                const _ConsentDetailRow(label: 'Documents', value: 'Aadhaar / Verified Evidence'),
                const SizedBox(height: 10),
                const _ConsentDetailRow(label: 'Destination', value: 'State & Central Government Portal'),
              ],
            ),
          ),
          const Spacer(),

          if (_errorMessage != null) ...[
            Text(
              _errorMessage!,
              style: const TextStyle(color: JanSetuTokens.rosePrimary, fontSize: 13),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
          ],

          // Buttons
          GoldButton(
            text: l10n.text('consent.grant'),
            isLoading: _isProcessing,
            icon: Icons.check_circle_rounded,
            onPressed: _handleGrantConsent,
          ),
          const SizedBox(height: 12),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              l10n.text('consent.reviewAgain'),
              style: const TextStyle(color: JanSetuTokens.textSecondary, fontSize: 14),
            ),
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}

class _ConsentDetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _ConsentDetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 90,
          child: Text(
            label,
            style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12, fontWeight: FontWeight.w500),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 13, fontWeight: FontWeight.w600),
          ),
        ),
      ],
    );
  }
}
