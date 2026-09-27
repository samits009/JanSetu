import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'agent/agent_screen.dart';
import 'applications/applications_screen.dart';
import 'auth/auth_screen.dart';
import 'benefits/benefits_screen.dart';
import 'core/config/app_config.dart';
import 'core/localization/app_localizations.dart';
import 'core/models/models.dart';
import 'core/networking/api_client.dart';
import 'core/repositories/agent_repository.dart';
import 'core/repositories/auth_repository.dart';
import 'core/repositories/citizen_repository.dart';
import 'core/storage/secure_storage.dart';
import 'core/theme/theme.dart';
import 'core/theme/tokens.dart';
import 'documents/documents_screen.dart';
import 'home/home_screen.dart';
import 'onboarding/onboarding_screen.dart';
import 'profile/profile_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final storageService = StorageService();
  await storageService.init();

  final apiClient = ApiClient(storageService: storageService);
  final authRepository = AuthRepository(apiClient: apiClient, storageService: storageService);
  final citizenRepository = CitizenRepository(apiClient: apiClient);
  final agentRepository = AgentRepository(apiClient: apiClient);

  runApp(
    JanSetuApp(
      storageService: storageService,
      authRepository: authRepository,
      citizenRepository: citizenRepository,
      agentRepository: agentRepository,
    ),
  );
}

class JanSetuApp extends StatefulWidget {
  final StorageService storageService;
  final AuthRepository authRepository;
  final CitizenRepository citizenRepository;
  final AgentRepository agentRepository;

  const JanSetuApp({
    super.key,
    required this.storageService,
    required this.authRepository,
    required this.citizenRepository,
    required this.agentRepository,
  });

  @override
  State<JanSetuApp> createState() => _JanSetuAppState();
}

class _JanSetuAppState extends State<JanSetuApp> {
  Locale _locale = const Locale('hi');
  bool _isInitializing = true;
  AuthResponseModel? _currentUser;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    // 1. Restore persisted language
    final savedLang = await widget.storageService.getLanguage();
    setState(() {
      _locale = Locale(savedLang);
    });

    // 2. Restore session securely from existing FastAPI backend
    try {
      final user = await widget.authRepository.restoreSession();
      if (mounted) {
        setState(() {
          _currentUser = user;
          if (user != null && user.preferredLanguage.isNotEmpty) {
            _locale = Locale(user.preferredLanguage);
          }
          _isInitializing = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _currentUser = null;
          _isInitializing = false;
        });
      }
    }
  }

  void _handleLanguageToggle() async {
    final nextLang = _locale.languageCode == 'hi' ? 'en' : 'hi';
    setState(() {
      _locale = Locale(nextLang);
    });
    await widget.authRepository.updateLanguagePreference(nextLang);
  }

  void _handleAuthenticated() async {
    final user = await widget.authRepository.restoreSession();
    setState(() {
      _currentUser = user;
    });
  }

  void _handleLogout() {
    setState(() {
      _currentUser = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: JanSetuTheme.darkTheme,
      locale: _locale,
      supportedLocales: const [
        Locale('hi'),
        Locale('en'),
      ],
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      home: _buildHomeWidget(),
    );
  }

  Widget _buildHomeWidget() {
    if (_isInitializing) {
      return const Scaffold(
        backgroundColor: JanSetuTokens.bgDeep,
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.account_balance_rounded, color: JanSetuTokens.goldPrimary, size: 48),
              SizedBox(height: 16),
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(JanSetuTokens.goldPrimary),
              ),
            ],
          ),
        ),
      );
    }

    // 1. Not Authenticated
    if (_currentUser == null || !_currentUser!.authenticated) {
      return AuthScreen(
        authRepository: widget.authRepository,
        onAuthenticated: _handleAuthenticated,
        onLanguageToggle: _handleLanguageToggle,
      );
    }

    // 2. Authenticated but Incomplete Onboarding
    if (!_currentUser!.onboardingCompleted) {
      return OnboardingScreen(
        citizenRepository: widget.citizenRepository,
        initialStep: _currentUser!.onboardingStep,
        onCompleted: () async {
          final refreshed = await widget.authRepository.restoreSession();
          setState(() {
            _currentUser = refreshed;
          });
        },
      );
    }

    // 3. Fully Authenticated Main Experience
    return MainShellScreen(
      citizenRepository: widget.citizenRepository,
      authRepository: widget.authRepository,
      agentRepository: widget.agentRepository,
      onLogout: _handleLogout,
      onLanguageChanged: _handleLanguageToggle,
    );
  }
}

class MainShellScreen extends StatefulWidget {
  final CitizenRepository citizenRepository;
  final AuthRepository authRepository;
  final AgentRepository agentRepository;
  final VoidCallback onLogout;
  final VoidCallback onLanguageChanged;

  const MainShellScreen({
    super.key,
    required this.citizenRepository,
    required this.authRepository,
    required this.agentRepository,
    required this.onLogout,
    required this.onLanguageChanged,
  });

  @override
  State<MainShellScreen> createState() => _MainShellScreenState();
}

class _MainShellScreenState extends State<MainShellScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    final screens = [
      HomeScreen(
        citizenRepository: widget.citizenRepository,
        onNavigateTab: (idx) => setState(() => _currentIndex = idx),
        onSelectScheme: () => setState(() => _currentIndex = 1),
      ),
      BenefitsScreen(
        citizenRepository: widget.citizenRepository,
        onPrepareApplication: (schemeId) {
          // Prepare application and jump to Applications tab
          widget.citizenRepository.prepareApplication(schemeId).then((_) {
            if (mounted) setState(() => _currentIndex = 3);
          });
        },
      ),
      DocumentsScreen(citizenRepository: widget.citizenRepository),
      ApplicationsScreen(citizenRepository: widget.citizenRepository),
      AgentScreen(agentRepository: widget.agentRepository),
      ProfileScreen(
        citizenRepository: widget.citizenRepository,
        authRepository: widget.authRepository,
        onLogout: widget.onLogout,
        onLanguageChanged: widget.onLanguageChanged,
      ),
    ];

    return Scaffold(
      backgroundColor: JanSetuTokens.bgDeep,
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: JanSetuTokens.bgSurface.withOpacity(0.95),
          border: const Border(
            top: BorderSide(color: JanSetuTokens.glassBorder, width: 1),
          ),
        ),
        child: SafeArea(
          child: NavigationBar(
            selectedIndex: _currentIndex,
            backgroundColor: Colors.transparent,
            indicatorColor: JanSetuTokens.goldPrimary.withOpacity(0.2),
            onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
            destinations: [
              NavigationDestination(
                icon: const Icon(Icons.home_outlined, color: JanSetuTokens.textMuted),
                selectedIcon: const Icon(Icons.home_rounded, color: JanSetuTokens.goldPrimary),
                label: l10n.text('nav.home'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.assignment_outlined, color: JanSetuTokens.textMuted),
                selectedIcon: const Icon(Icons.assignment_rounded, color: JanSetuTokens.goldPrimary),
                label: l10n.text('nav.benefits'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.folder_outlined, color: JanSetuTokens.textMuted),
                selectedIcon: const Icon(Icons.folder_rounded, color: JanSetuTokens.goldPrimary),
                label: l10n.text('nav.documents'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.layers_outlined, color: JanSetuTokens.textMuted),
                selectedIcon: const Icon(Icons.layers_rounded, color: JanSetuTokens.goldPrimary),
                label: l10n.text('nav.applications'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.smart_toy_outlined, color: JanSetuTokens.textMuted),
                selectedIcon: const Icon(Icons.smart_toy_rounded, color: JanSetuTokens.goldPrimary),
                label: l10n.text('nav.agent'),
              ),
              NavigationDestination(
                icon: const Icon(Icons.person_outline, color: JanSetuTokens.textMuted),
                selectedIcon: const Icon(Icons.person_rounded, color: JanSetuTokens.goldPrimary),
                label: l10n.text('nav.profile'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
