import 'package:flutter/material.dart';
import '../core/data/india_locations.dart';
import '../core/localization/app_localizations.dart';
import '../core/repositories/citizen_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';
import '../shared/widgets/glass_select.dart';
import '../shared/widgets/gold_button.dart';

class OnboardingScreen extends StatefulWidget {
  final CitizenRepository citizenRepository;
  final int initialStep;
  final VoidCallback onCompleted;

  const OnboardingScreen({
    super.key,
    required this.citizenRepository,
    this.initialStep = 1,
    required this.onCompleted,
  });

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  late int _currentStep;
  bool _isLoading = false;
  String? _errorMessage;

  // Step 1: Personal
  final _nameController = TextEditingController();
  final _dobController = TextEditingController(text: '1995-01-01');
  String _gender = 'MALE';
  String _casteCategory = 'GENERAL';

  // Step 2: Location
  String? _currentState = 'Uttar Pradesh';
  String? _currentDistrict = 'Gorakhpur';
  String? _permanentState = 'Uttar Pradesh';
  String? _permanentDistrict = 'Gorakhpur';
  bool _isMigrant = false;

  // Step 3: Employment
  final _occupationController = TextEditingController(text: 'Agricultural Worker');
  String _employmentStatus = 'EMPLOYED';
  final _incomeController = TextEditingController(text: '120000');
  bool _hasDisability = false;

  // Step 4: Household
  int _householdMembersCount = 4;
  int _childrenCount = 2;

  @override
  void initState() {
    super.initState();
    _currentStep = widget.initialStep.clamp(1, 4);
    _loadExistingProfile();
  }

  Future<void> _loadExistingProfile() async {
    try {
      final profile = await widget.citizenRepository.getMyProfile();
      if (profile.isNotEmpty) {
        setState(() {
          if (profile['name'] != null) _nameController.text = profile['name'].toString();
          if (profile['dob'] != null) _dobController.text = profile['dob'].toString();
          if (profile['gender'] != null) _gender = profile['gender'].toString().toUpperCase();
          if (profile['onboarding_step'] is int && profile['onboarding_step'] > _currentStep) {
            _currentStep = profile['onboarding_step'];
          }
        });
      }
    } catch (_) {
      // Continue with clean state
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _dobController.dispose();
    _occupationController.dispose();
    _incomeController.dispose();
    super.dispose();
  }

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
    return districts
        .map((d) => GlassSelectOption(value: d, label: d, group: stateName))
        .toList();
  }

  Future<void> _handleNextStep() async {
    setState(() {
      _errorMessage = null;
      _isLoading = true;
    });

    try {
      // Validate step syntax
      if (_currentStep == 1 && _nameController.text.trim().isEmpty) {
        throw Exception('Please enter your full legal name');
      }
      if (_currentStep == 2) {
        if (_currentState == null || _currentDistrict == null) {
          throw Exception('Please select your current state and district');
        }
      }

      // Persist step through existing FastAPI backend
      final income = double.tryParse(_incomeController.text.trim()) ?? 0.0;
      await widget.citizenRepository.saveOnboardingStep(
        step: _currentStep,
        name: _currentStep == 1 ? _nameController.text.trim() : null,
        dob: _currentStep == 1 ? _dobController.text.trim() : null,
        gender: _currentStep == 1 ? _gender : null,
        currentState: _currentStep == 2 ? _currentState : null,
        currentDistrict: _currentStep == 2 ? _currentDistrict : null,
        permanentState: _currentStep == 2 ? _permanentState : null,
        permanentDistrict: _currentStep == 2 ? _permanentDistrict : null,
        occupation: _currentStep == 3 ? _occupationController.text.trim() : null,
        employmentStatus: _currentStep == 3 ? _employmentStatus : null,
        annualIncome: _currentStep == 3 ? income : null,
        householdMembersCount: _currentStep == 4 ? _householdMembersCount : null,
        childrenCount: _currentStep == 4 ? _childrenCount : null,
      );

      if (_currentStep < 4) {
        setState(() {
          _currentStep++;
        });
      } else {
        // Step 4 complete: finalize onboarding
        await widget.citizenRepository.completeOnboarding();
        widget.onCompleted();
      }
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
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 560),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Top Progress Pathway
                Row(
                  children: [
                    for (int i = 1; i <= 4; i++) ...[
                      Expanded(
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          height: 4,
                          decoration: BoxDecoration(
                            color: i <= _currentStep
                                ? JanSetuTokens.goldPrimary
                                : JanSetuTokens.glassBorderSubtle,
                            borderRadius: BorderRadius.circular(2),
                            boxShadow: i <= _currentStep ? JanSetuTokens.goldGlowShadow : null,
                          ),
                        ),
                      ),
                      if (i < 4) const SizedBox(width: 8),
                    ],
                  ],
                ),
                const SizedBox(height: 16),

                // Step Indicator Badge
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: JanSetuTokens.goldPrimary.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: JanSetuTokens.goldPrimary.withOpacity(0.4)),
                      ),
                      child: Text(
                        'STEP $_currentStep OF 4',
                        style: const TextStyle(
                          color: JanSetuTokens.goldPrimary,
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.8,
                        ),
                      ),
                    ),
                    const Spacer(),
                    if (_currentStep > 1)
                      TextButton.icon(
                        onPressed: () {
                          setState(() {
                            _currentStep--;
                            _errorMessage = null;
                          });
                        },
                        icon: const Icon(Icons.arrow_back_rounded, size: 16, color: JanSetuTokens.textSecondary),
                        label: Text(
                          l10n.text('common.back'),
                          style: const TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 12),

                // Onboarding Title & Description
                Text(
                  _getStepTitle(l10n),
                  style: const TextStyle(
                    color: JanSetuTokens.textPrimary,
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  _getStepSubtitle(l10n),
                  style: const TextStyle(
                    color: JanSetuTokens.textSecondary,
                    fontSize: 13,
                    height: 1.45,
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
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: JanSetuTokens.rosePrimary, fontSize: 13),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Step Content Card
                GlassCard(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (_currentStep == 1) _buildStep1Personal(l10n),
                      if (_currentStep == 2) _buildStep2Location(l10n),
                      if (_currentStep == 3) _buildStep3Employment(l10n),
                      if (_currentStep == 4) _buildStep4Household(l10n),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Forward Action
                GoldButton(
                  text: _currentStep == 4 ? l10n.text('onboarding.complete') : l10n.text('common.next'),
                  icon: _currentStep == 4 ? Icons.check_circle_rounded : Icons.arrow_forward_rounded,
                  isLoading: _isLoading,
                  onPressed: _handleNextStep,
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _getStepTitle(AppLocalizations l10n) {
    switch (_currentStep) {
      case 1:
        return 'Personal Identity';
      case 2:
        return 'Location & Residence';
      case 3:
        return 'Employment & Livelihood';
      case 4:
        return 'Household & Dependents';
      default:
        return l10n.text('onboarding.title');
    }
  }

  String _getStepSubtitle(AppLocalizations l10n) {
    switch (_currentStep) {
      case 1:
        return 'Enter legal name and basic demographics for statutory scheme qualification.';
      case 2:
        return 'Select current and permanent residence using all 28 Indian States and 8 UTs.';
      case 3:
        return 'Your occupation and household income directly determine state and central scheme entitlement.';
      case 4:
        return 'Family composition unlocks targeted child, senior citizen, and ration allowances.';
      default:
        return '';
    }
  }

  Widget _buildStep1Personal(AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.text('onboarding.name'),
          style: const TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: _nameController,
          style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 15),
          decoration: InputDecoration(
            hintText: l10n.text('onboarding.nameHint'),
            prefixIcon: const Icon(Icons.badge_outlined, color: JanSetuTokens.goldPrimary, size: 20),
          ),
        ),
        const SizedBox(height: 18),

        Text(
          l10n.text('onboarding.dob'),
          style: const TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: _dobController,
          style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 15),
          decoration: const InputDecoration(
            hintText: 'YYYY-MM-DD',
            prefixIcon: Icon(Icons.calendar_today_outlined, color: JanSetuTokens.goldPrimary, size: 20),
          ),
        ),
        const SizedBox(height: 18),

        GlassSelect(
          label: l10n.text('onboarding.gender'),
          value: _gender,
          placeholder: 'Select Gender',
          prefixIcon: Icons.wc_rounded,
          options: [
            GlassSelectOption(value: 'MALE', label: l10n.text('onboarding.genderMale')),
            GlassSelectOption(value: 'FEMALE', label: l10n.text('onboarding.genderFemale')),
            GlassSelectOption(value: 'OTHER', label: l10n.text('onboarding.genderOther')),
          ],
          onChanged: (val) {
            if (val != null) setState(() => _gender = val);
          },
        ),
        const SizedBox(height: 18),

        GlassSelect(
          label: l10n.text('onboarding.caste'),
          value: _casteCategory,
          placeholder: 'Select Social Category',
          prefixIcon: Icons.group_work_outlined,
          options: [
            GlassSelectOption(value: 'GENERAL', label: l10n.text('onboarding.casteGeneral')),
            GlassSelectOption(value: 'OBC', label: l10n.text('onboarding.casteOBC')),
            GlassSelectOption(value: 'SC', label: l10n.text('onboarding.casteSC')),
            GlassSelectOption(value: 'ST', label: l10n.text('onboarding.casteST')),
          ],
          onChanged: (val) {
            if (val != null) setState(() => _casteCategory = val);
          },
        ),
      ],
    );
  }

  Widget _buildStep2Location(AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Current State
        GlassSelect(
          label: l10n.text('onboarding.currentState'),
          value: _currentState,
          placeholder: 'Select State or UT',
          prefixIcon: Icons.location_on_outlined,
          options: _getStateOptions(),
          onChanged: (newState) {
            setState(() {
              _currentState = newState;
              // Clear invalid district per Non-Negotiable Rule
              final validDistricts = IndiaLocations.getDistrictsFor(newState);
              if (!validDistricts.contains(_currentDistrict)) {
                _currentDistrict = validDistricts.isNotEmpty ? validDistricts.first : null;
              }
            });
          },
        ),
        const SizedBox(height: 18),

        // Current District (Dynamic cascade)
        GlassSelect(
          label: l10n.text('onboarding.currentDistrict'),
          value: _currentDistrict,
          placeholder: _currentState != null ? 'Select District' : 'First select State above',
          enabled: _currentState != null,
          prefixIcon: Icons.map_outlined,
          options: _getDistrictOptions(_currentState),
          onChanged: (newDistrict) {
            setState(() => _currentDistrict = newDistrict);
          },
        ),
        const SizedBox(height: 18),

        // Permanent State
        GlassSelect(
          label: l10n.text('onboarding.permanentState'),
          value: _permanentState,
          placeholder: 'Select Home State',
          prefixIcon: Icons.home_work_outlined,
          options: _getStateOptions(),
          onChanged: (newState) {
            setState(() {
              _permanentState = newState;
              final validDistricts = IndiaLocations.getDistrictsFor(newState);
              if (!validDistricts.contains(_permanentDistrict)) {
                _permanentDistrict = validDistricts.isNotEmpty ? validDistricts.first : null;
              }
            });
          },
        ),
        const SizedBox(height: 18),

        // Permanent District
        GlassSelect(
          label: l10n.text('onboarding.permanentDistrict'),
          value: _permanentDistrict,
          placeholder: _permanentState != null ? 'Select Home District' : 'First select Home State',
          enabled: _permanentState != null,
          prefixIcon: Icons.my_location_rounded,
          options: _getDistrictOptions(_permanentState),
          onChanged: (newDistrict) {
            setState(() => _permanentDistrict = newDistrict);
          },
        ),
        const SizedBox(height: 18),

        // Migrant toggle
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: Text(
            l10n.text('onboarding.isMigrant'),
            style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14),
          ),
          value: _isMigrant,
          activeColor: JanSetuTokens.goldPrimary,
          onChanged: (val) => setState(() => _isMigrant = val),
        ),
      ],
    );
  }

  Widget _buildStep3Employment(AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.text('onboarding.occupation'),
          style: const TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: _occupationController,
          style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 15),
          decoration: const InputDecoration(
            hintText: 'e.g. Construction Worker, Farmer, Street Vendor',
            prefixIcon: Icon(Icons.work_outline_rounded, color: JanSetuTokens.goldPrimary, size: 20),
          ),
        ),
        const SizedBox(height: 18),

        GlassSelect(
          label: l10n.text('onboarding.occupationSector'),
          value: _employmentStatus,
          placeholder: 'Select Status',
          prefixIcon: Icons.business_center_outlined,
          options: const [
            GlassSelectOption(value: 'EMPLOYED', label: 'Employed (Informal / Daily Wage)'),
            GlassSelectOption(value: 'FORMAL', label: 'Formal Sector Employee'),
            GlassSelectOption(value: 'SELF_EMPLOYED', label: 'Self Employed / Artisan'),
            GlassSelectOption(value: 'UNEMPLOYED', label: 'Unemployed / Seeking Work'),
          ],
          onChanged: (val) {
            if (val != null) setState(() => _employmentStatus = val);
          },
        ),
        const SizedBox(height: 18),

        Text(
          l10n.text('onboarding.monthlyIncome'),
          style: const TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: _incomeController,
          keyboardType: TextInputType.number,
          style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 15),
          decoration: const InputDecoration(
            hintText: 'e.g. 120000',
            prefixIcon: Icon(Icons.currency_rupee_rounded, color: JanSetuTokens.goldPrimary, size: 20),
          ),
        ),
        const SizedBox(height: 18),

        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: Text(
            l10n.text('onboarding.hasDisability'),
            style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14),
          ),
          value: _hasDisability,
          activeColor: JanSetuTokens.goldPrimary,
          onChanged: (val) => setState(() => _hasDisability = val),
        ),
      ],
    );
  }

  Widget _buildStep4Household(AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Total Household Members',
          style: TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            IconButton(
              icon: const Icon(Icons.remove_circle_outline, color: JanSetuTokens.goldPrimary, size: 28),
              onPressed: _householdMembersCount > 1
                  ? () => setState(() => _householdMembersCount--)
                  : null,
            ),
            Text(
              '$_householdMembersCount Persons',
              style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 18, fontWeight: FontWeight.w700),
            ),
            IconButton(
              icon: const Icon(Icons.add_circle_outline, color: JanSetuTokens.goldPrimary, size: 28),
              onPressed: () => setState(() => _householdMembersCount++),
            ),
          ],
        ),
        const SizedBox(height: 20),

        const Text(
          'Minor Children / Dependents',
          style: TextStyle(color: JanSetuTokens.textSecondary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            IconButton(
              icon: const Icon(Icons.remove_circle_outline, color: JanSetuTokens.goldPrimary, size: 28),
              onPressed: _childrenCount > 0
                  ? () => setState(() => _childrenCount--)
                  : null,
            ),
            Text(
              '$_childrenCount Children',
              style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 18, fontWeight: FontWeight.w700),
            ),
            IconButton(
              icon: const Icon(Icons.add_circle_outline, color: JanSetuTokens.goldPrimary, size: 28),
              onPressed: () => setState(() => _childrenCount++),
            ),
          ],
        ),
      ],
    );
  }
}
