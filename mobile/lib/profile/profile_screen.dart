import 'package:flutter/material.dart';
import '../core/data/india_locations.dart';
import '../core/localization/app_localizations.dart';
import '../core/repositories/auth_repository.dart';
import '../core/repositories/citizen_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';
import '../shared/widgets/glass_select.dart';
import '../shared/widgets/gold_button.dart';

class ProfileScreen extends StatefulWidget {
  final CitizenRepository citizenRepository;
  final AuthRepository authRepository;
  final VoidCallback onLogout;
  final VoidCallback onLanguageChanged;

  const ProfileScreen({
    super.key,
    required this.citizenRepository,
    required this.authRepository,
    required this.onLogout,
    required this.onLanguageChanged,
  });

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  Map<String, dynamic>? _profile;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final p = await widget.citizenRepository.getMyProfile();
      if (mounted) {
        setState(() {
          _profile = p;
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

  void _openRelocationSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _RelocationSheet(
        citizenRepository: widget.citizenRepository,
        onRelocated: () {
          Navigator.pop(ctx);
          _fetchProfile();
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return CinematicScaffold(
      body: RefreshIndicator(
        onRefresh: _fetchProfile,
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
                l10n.text('nav.profile'),
                style: const TextStyle(
                  color: JanSetuTokens.textPrimary,
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
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
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: JanSetuTokens.rosePrimary.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: JanSetuTokens.rosePrimary.withOpacity(0.4)),
                  ),
                  child: Text(
                    _errorMessage!,
                    style: const TextStyle(color: JanSetuTokens.rosePrimary, fontSize: 13),
                  ),
                ),
                const SizedBox(height: 16),
              ] else if (_profile != null) ...[
                // Profile Avatar & Name Card
                GlassCard(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    children: [
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: JanSetuTokens.goldPrimary.withOpacity(0.15),
                          border: Border.all(color: JanSetuTokens.goldPrimary.withOpacity(0.5)),
                        ),
                        child: const Icon(Icons.person_rounded, color: JanSetuTokens.goldPrimary, size: 30),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _profile?['name']?.toString() ?? 'Citizen',
                              style: const TextStyle(
                                color: JanSetuTokens.textPrimary,
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              _profile?['phone']?.toString() ?? _profile?['email']?.toString() ?? 'Verified Identity',
                              style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 13),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Life Changes ("Something Changed?")
                GlassCard(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.swap_horiz_rounded, color: JanSetuTokens.goldPrimary, size: 20),
                          const SizedBox(width: 8),
                          const Text(
                            'Something Changed?',
                            style: TextStyle(
                              color: JanSetuTokens.textPrimary,
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Relocating to another state or changing employment recalculates your state and central welfare entitlements instantly.',
                        style: TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13, height: 1.4),
                      ),
                      const SizedBox(height: 14),
                      OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: JanSetuTokens.goldPrimary,
                          side: const BorderSide(color: JanSetuTokens.goldPrimary),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        icon: const Icon(Icons.place_outlined, size: 18),
                        label: const Text('I Moved (Relocation Survival Check)'),
                        onPressed: _openRelocationSheet,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Demographics Details Card
                GlassCard(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Citizen Welfare Profile',
                        style: TextStyle(
                          color: JanSetuTokens.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 16),
                      _ProfileRow(label: 'Gender', value: _profile?['gender']?.toString() ?? 'N/A'),
                      const SizedBox(height: 10),
                      _ProfileRow(label: 'Date of Birth', value: _profile?['dob']?.toString() ?? 'N/A'),
                      const SizedBox(height: 10),
                      _ProfileRow(label: 'Social Category', value: _profile?['caste_category']?.toString() ?? 'General'),
                      const SizedBox(height: 10),
                      _ProfileRow(label: 'Current Residence', value: '${_profile?['current_district'] ?? 'N/A'}, ${_profile?['current_state'] ?? ''}'),
                      const SizedBox(height: 10),
                      _ProfileRow(label: 'Home State', value: '${_profile?['permanent_district'] ?? 'N/A'}, ${_profile?['permanent_state'] ?? ''}'),
                      const SizedBox(height: 10),
                      _ProfileRow(label: 'Occupation', value: _profile?['occupation']?.toString() ?? 'N/A'),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Preferences & Language Card
                GlassCard(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Language & Preferences',
                        style: TextStyle(
                          color: JanSetuTokens.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Application Language',
                            style: TextStyle(color: JanSetuTokens.textSecondary, fontSize: 14),
                          ),
                          InkWell(
                            onTap: () async {
                              final newLang = l10n.isHindi ? 'en' : 'hi';
                              await widget.authRepository.updateLanguagePreference(newLang);
                              widget.onLanguageChanged();
                            },
                            borderRadius: BorderRadius.circular(10),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                              decoration: BoxDecoration(
                                color: JanSetuTokens.goldPrimary.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: JanSetuTokens.goldPrimary.withOpacity(0.3)),
                              ),
                              child: Text(
                                l10n.isHindi ? 'हिंदी (Switch to EN)' : 'English (Switch to हिंदी)',
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
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Logout Button
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: JanSetuTokens.rosePrimary,
                    side: BorderSide(color: JanSetuTokens.rosePrimary.withOpacity(0.5)),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  icon: const Icon(Icons.logout_rounded, size: 20),
                  label: Text(
                    l10n.text('nav.logout'),
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
                  ),
                  onPressed: () async {
                    await widget.authRepository.logout();
                    widget.onLogout();
                  },
                ),
                const SizedBox(height: 24),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _ProfileRow extends StatelessWidget {
  final String label;
  final String value;

  const _ProfileRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 13),
        ),
        Text(
          value,
          style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
      ],
    );
  }
}

class _RelocationSheet extends StatefulWidget {
  final CitizenRepository citizenRepository;
  final VoidCallback onRelocated;

  const _RelocationSheet({
    required this.citizenRepository,
    required this.onRelocated,
  });

  @override
  State<_RelocationSheet> createState() => _RelocationSheetState();
}

class _RelocationSheetState extends State<_RelocationSheet> {
  String? _selectedState = 'Delhi NCR';
  String? _selectedDistrict = 'New Delhi';
  bool _isSimulating = false;
  Map<String, dynamic>? _simulationResult;

  List<GlassSelectOption> _getStateOptions() {
    final options = <GlassSelectOption>[];
    for (final s in IndiaLocations.states) {
      options.add(GlassSelectOption(value: s, label: s, group: 'States (28)'));
    }
    for (final ut in IndiaLocations.unionTerritories) {
      options.add(GlassSelectOption(value: ut, label: ut, group: 'Union Territories (8)'));
    }
    return options;
  }

  List<GlassSelectOption> _getDistrictOptions(String? stateName) {
    if (stateName == null || stateName.isEmpty) return const [];
    final districts = IndiaLocations.getDistrictsFor(stateName);
    return districts.map((d) => GlassSelectOption(value: d, label: d, group: stateName)).toList();
  }

  Future<void> _simulateRelocation() async {
    if (_selectedState == null || _selectedDistrict == null) return;

    setState(() {
      _isSimulating = true;
    });

    try {
      final res = await widget.citizenRepository.relocateCitizen(
        newState: _selectedState!,
        newDistrict: _selectedDistrict!,
      );
      setState(() {
        _simulationResult = res;
        _isSimulating = false;
      });
    } catch (_) {
      setState(() {
        _isSimulating = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.75,
      decoration: BoxDecoration(
        color: JanSetuTokens.bgSurface.withOpacity(0.96),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        border: const Border(top: BorderSide(color: JanSetuTokens.goldPrimary, width: 2)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
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
          const SizedBox(height: 16),
          const Text(
            'Inter-State Welfare Recalculation',
            style: TextStyle(color: JanSetuTokens.textPrimary, fontSize: 18, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          const Text(
            'Select your new destination state and district to calculate which state benefits stay protected and which new local schemes become active.',
            style: TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13),
          ),
          const SizedBox(height: 20),

          GlassSelect(
            label: 'Destination State / UT',
            value: _selectedState,
            placeholder: 'Select Destination State',
            options: _getStateOptions(),
            onChanged: (s) {
              setState(() {
                _selectedState = s;
                final dists = IndiaLocations.getDistrictsFor(s);
                _selectedDistrict = dists.isNotEmpty ? dists.first : null;
              });
            },
          ),
          const SizedBox(height: 14),

          GlassSelect(
            label: 'Destination District',
            value: _selectedDistrict,
            placeholder: 'Select Destination District',
            options: _getDistrictOptions(_selectedState),
            onChanged: (d) => setState(() => _selectedDistrict = d),
          ),
          const SizedBox(height: 20),

          GoldButton(
            text: 'Calculate Welfare Impact',
            icon: Icons.calculate_outlined,
            isLoading: _isSimulating,
            onPressed: _simulateRelocation,
          ),
          const SizedBox(height: 16),

          if (_simulationResult != null) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: JanSetuTokens.bgDeep.withOpacity(0.7),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: JanSetuTokens.emeraldPrimary.withOpacity(0.4)),
              ),
              child: const Text(
                '✓ Central Portable Benefits (e.g. One Nation One Ration, PM-JAY, PM-SVANidhi) remain 100% active and protected at new location.',
                style: TextStyle(color: JanSetuTokens.emeraldPrimary, fontSize: 13),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
