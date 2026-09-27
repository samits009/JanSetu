import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';

enum Environment {
  development,
  test,
  production,
}

class AppConfig {
  static const String appName = 'JanSetu';
  static const String appTagline = 'The Sovereign Citizen Welfare Bridge of India';
  static const String appTaglineHi = 'भारत का संप्रभु नागरिक कल्याण सेतु';
  static const String version = '1.0.0+1';

  // Environment override passed via: flutter run --dart-define=JANSETU_ENV=production
  static const String _envString = String.fromEnvironment(
    'JANSETU_ENV',
    defaultValue: 'development',
  );

  // Custom API URL override via: flutter run --dart-define=JANSETU_API_URL=https://api.jansetu.gov.in
  static const String _customApiUrl = String.fromEnvironment('JANSETU_API_URL');

  static Environment get environment {
    switch (_envString.toLowerCase()) {
      case 'production':
      case 'prod':
        return Environment.production;
      case 'test':
        return Environment.test;
      case 'development':
      case 'dev':
      default:
        return kReleaseMode ? Environment.production : Environment.development;
    }
  }

  /// Centralized API Base URL
  /// Strictly adheres to NON-NEGOTIABLE RULE 15: No production localhost URLs.
  static String get apiBaseUrl {
    if (_customApiUrl.isNotEmpty) {
      return _customApiUrl;
    }

    switch (environment) {
      case Environment.production:
        // Production HTTPS endpoint
        return 'https://api.jansetu.in';

      case Environment.test:
        return 'https://test-api.jansetu.in';

      case Environment.development:
        // When running in development mode on local devices:
        if (kIsWeb) {
          return 'http://127.0.0.1:8000';
        }
        try {
          if (Platform.isAndroid) {
            // Android emulator loopback alias to host machine
            return 'http://10.0.2.2:8000';
          } else if (Platform.isIOS || Platform.isMacOS || Platform.isWindows || Platform.isLinux) {
            return 'http://127.0.0.1:8000';
          }
        } catch (_) {
          // Fallback if Platform is not available
        }
        return 'http://10.0.2.2:8000';
    }
  }

  static Duration get connectTimeout => const Duration(seconds: 15);
  static Duration get receiveTimeout => const Duration(seconds: 30);
}
