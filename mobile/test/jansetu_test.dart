import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/core/data/india_locations.dart';
import 'package:mobile/core/errors/api_exception.dart';
import 'package:mobile/core/localization/app_localizations.dart';
import 'package:mobile/core/models/models.dart';
import 'package:mobile/shared/widgets/glass_card.dart';
import 'package:mobile/shared/widgets/glass_select.dart';
import 'package:mobile/shared/widgets/gold_button.dart';

void main() {
  group('Phase 9AC — JanSetu Data & Location Tests', () {
    test('IndiaLocations contains all 28 states and 8 union territories', () {
      expect(IndiaLocations.states.length, equals(28));
      expect(IndiaLocations.unionTerritories.length, equals(8));
      expect(IndiaLocations.all.length, equals(36));

      // Test specific key states
      expect(IndiaLocations.states, contains('Uttar Pradesh'));
      expect(IndiaLocations.states, contains('Bihar'));
      expect(IndiaLocations.states, contains('Maharashtra'));

      // Test specific union territories
      expect(IndiaLocations.unionTerritories, contains('Delhi NCR'));
      expect(IndiaLocations.unionTerritories, contains('Ladakh'));
    });

    test('Dynamic district cascading works accurately', () {
      final upDistricts = IndiaLocations.getDistrictsFor('Uttar Pradesh');
      expect(upDistricts, isNotEmpty);
      expect(upDistricts, contains('Gorakhpur'));
      expect(upDistricts, contains('Lucknow'));
      expect(upDistricts, contains('Varanasi'));

      final delhiDistricts = IndiaLocations.getDistrictsFor('Delhi NCR');
      expect(delhiDistricts, contains('New Delhi'));
      expect(delhiDistricts, contains('South Delhi'));

      // Invalid district checks
      expect(IndiaLocations.isValidDistrict('Uttar Pradesh', 'Gorakhpur'), isTrue);
      expect(IndiaLocations.isValidDistrict('Uttar Pradesh', 'New Delhi'), isFalse);
    });
  });

  group('Phase 9AC — Model Parsing Tests', () {
    test('AuthResponseModel parses backend payload accurately', () {
      final json = {
        'authenticated': true,
        'user_id': 'u-1234',
        'citizen_id': 'c-5678',
        'name': 'Samit Shukla',
        'email': 'samit@example.gov.in',
        'role': 'citizen',
        'preferred_language': 'hi',
        'onboarding_completed': true,
        'onboarding_step': 4,
        'session_token': 'sess-token-xyz',
      };

      final auth = AuthResponseModel.fromJson(json);
      expect(auth.authenticated, isTrue);
      expect(auth.userId, equals('u-1234'));
      expect(auth.citizenId, equals('c-5678'));
      expect(auth.preferredLanguage, equals('hi'));
      expect(auth.onboardingCompleted, isTrue);
      expect(auth.activeToken, equals('sess-token-xyz'));
    });

    test('WelfareStateModel parses live benefits and metrics', () {
      final json = {
        'citizen_id': 'c-123',
        'total_potential_monthly_benefit': 4500.0,
        'eligible_schemes_count': 3,
        'schemes_ready_to_apply': 2,
        'evidence_readiness_score': 0.85,
        'active_schemes': [
          {
            'id': 'pm-kisan-1',
            'code': 'PM-KISAN',
            'name': 'PM-KISAN Samman Nidhi',
            'name_hi': 'पीएम-किसान सम्मान निधि',
            'monthly_value': 500.0,
            'status': 'eligible',
            'readiness_score': 1.0,
            'match_reasons': ['Cultivable landholding', 'Citizen registered'],
            'required_documents': ['Aadhaar', 'Land Record'],
          },
        ],
        'recommended_actions': ['Upload Land Record certificate'],
      };

      final state = WelfareStateModel.fromJson(json);
      expect(state.totalPotentialMonthlyBenefit, equals(4500.0));
      expect(state.eligibleSchemesCount, equals(3));
      expect(state.evidenceReadinessScore, equals(0.85));
      expect(state.activeSchemes.length, equals(1));
      expect(state.activeSchemes.first.code, equals('PM-KISAN'));
      expect(state.activeSchemes.first.localizedName('hi'), equals('पीएम-किसान सम्मान निधि'));
      expect(state.activeSchemes.first.localizedName('en'), equals('PM-KISAN Samman Nidhi'));
    });
  });

  group('Phase 9AC — Localization Tests', () {
    test('Bilingual dictionary has parity across critical keys', () {
      final l10nEn = AppLocalizations(const Locale('en'));
      final l10nHi = AppLocalizations(const Locale('hi'));

      expect(l10nEn.text('nav.home'), equals('Home'));
      expect(l10nHi.text('nav.home'), equals('होम'));

      expect(l10nEn.text('auth.loginBtn'), equals('Access Welfare Portal'));
      expect(l10nHi.text('auth.loginBtn'), equals('कल्याण पोर्टल में प्रवेश करें'));

      expect(l10nEn.text('consent.readyToContinue'), equals('Ready to continue?'));
      expect(l10nHi.text('consent.readyToContinue'), equals('क्या आप आगे बढ़ना चाहते हैं?'));
    });
  });

  group('Phase 9AC — Error Hierarchy Tests', () {
    test('ApiException maps status codes to citizen-friendly errors', () {
      final e401 = ApiException.fromStatusCode(401);
      expect(e401, isA<UnauthorizedException>());
      expect(e401.localizedMessage('hi'), contains('सत्र समाप्त'));

      final e404 = ApiException.fromStatusCode(404);
      expect(e404, isA<NotFoundException>());

      final eNet = ApiException.networkError();
      expect(eNet, isA<NetworkException>());
      expect(eNet.localizedMessage('hi'), contains('इंटरनेट कनेक्शन नहीं है'));
    });
  });

  group('Phase 9AC — UI Widget Tests', () {
    testWidgets('GoldButton renders text and triggers callback', (tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: GoldButton(
              text: 'Access Portal',
              onPressed: () {
                tapped = true;
              },
            ),
          ),
        ),
      );

      expect(find.text('Access Portal'), findsOneWidget);
      await tester.tap(find.text('Access Portal'));
      expect(tapped, isTrue);
    });

    testWidgets('GlassCard renders child widget with frosted background', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: GlassCard(
              child: Text('Protected Citizen Record'),
            ),
          ),
        ),
      );

      expect(find.text('Protected Citizen Record'), findsOneWidget);
    });

    testWidgets('GlassSelect displays label and placeholder', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: GlassSelect(
              label: 'Current Residence',
              value: null,
              placeholder: 'Choose State',
              options: const [
                GlassSelectOption(value: 'UP', label: 'Uttar Pradesh'),
                GlassSelectOption(value: 'DL', label: 'Delhi NCR'),
              ],
              onChanged: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('Current Residence'), findsOneWidget);
      expect(find.text('Choose State'), findsOneWidget);
    });
  });
}
