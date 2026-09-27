import '../models/models.dart';
import '../networking/api_client.dart';
import '../storage/secure_storage.dart';

class AuthRepository {
  final ApiClient _apiClient;
  final StorageService _storageService;

  AuthRepository({
    required ApiClient apiClient,
    required StorageService storageService,
  })  : _apiClient = apiClient,
        _storageService = storageService;

  Future<AuthResponseModel> register({
    String? email,
    String? phone,
    required String password,
    String preferredLanguage = 'hi',
  }) async {
    final response = await _apiClient.post(
      '/api/auth/register',
      body: {
        'email': email,
        'phone': phone,
        'password': password,
        'preferred_language': preferredLanguage,
      },
    );

    final auth = AuthResponseModel.fromJson(response as Map<String, dynamic>);
    final token = auth.activeToken;
    if (token != null && token.isNotEmpty) {
      await _storageService.saveSessionToken(token);
    }
    await _storageService.saveLanguage(auth.preferredLanguage);
    return auth;
  }

  Future<AuthResponseModel> login({
    required String username,
    required String password,
  }) async {
    final response = await _apiClient.post(
      '/api/auth/login',
      body: {
        'username': username,
        'password': password,
      },
    );

    final auth = AuthResponseModel.fromJson(response as Map<String, dynamic>);
    final token = auth.activeToken;
    if (token != null && token.isNotEmpty) {
      await _storageService.saveSessionToken(token);
    }
    await _storageService.saveLanguage(auth.preferredLanguage);
    return auth;
  }

  Future<AuthResponseModel?> restoreSession() async {
    final token = await _storageService.getSessionToken();
    if (token == null || token.isEmpty) {
      return null;
    }

    try {
      final response = await _apiClient.get('/api/auth/me');
      final auth = AuthResponseModel.fromJson(response as Map<String, dynamic>);
      if (auth.authenticated) {
        await _storageService.saveLanguage(auth.preferredLanguage);
        return auth;
      }
      return null;
    } catch (_) {
      // If token expired or network unreachable with 401, clear token
      return null;
    }
  }

  Future<void> logout() async {
    try {
      await _apiClient.post('/api/auth/logout');
    } catch (_) {
      // Best-effort server notification
    }
    await _storageService.clearSessionToken();
  }

  Future<void> updateLanguagePreference(String languageCode) async {
    await _storageService.saveLanguage(languageCode);
    try {
      await _apiClient.put(
        '/api/auth/me/preferences',
        body: {'preferred_language': languageCode},
      );
    } catch (_) {
      // Ignore if offline, preference is saved locally and will sync
    }
  }
}
