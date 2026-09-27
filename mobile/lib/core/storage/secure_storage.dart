import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _keySessionToken = 'jansetu_session_token';
  static const String _keyLanguage = 'jansetu_pref_language';
  static const String _keyOfflineProfile = 'jansetu_cache_profile';

  final FlutterSecureStorage _secureStorage;
  SharedPreferences? _prefs;

  StorageService({FlutterSecureStorage? secureStorage})
      : _secureStorage = secureStorage ?? const FlutterSecureStorage();

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // --- Session Token Management ---
  Future<void> saveSessionToken(String token) async {
    await _secureStorage.write(key: _keySessionToken, value: token);
  }

  Future<String?> getSessionToken() async {
    return await _secureStorage.read(key: _keySessionToken);
  }

  Future<void> clearSessionToken() async {
    await _secureStorage.delete(key: _keySessionToken);
  }

  // --- Preferred Language (Default 'hi') ---
  Future<void> saveLanguage(String lang) async {
    _prefs ??= await SharedPreferences.getInstance();
    await _prefs!.setString(_keyLanguage, lang);
  }

  Future<String> getLanguage() async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!.getString(_keyLanguage) ?? 'hi';
  }

  // --- Cached Offline Profile Data ---
  Future<void> saveCachedProfile(String jsonString) async {
    _prefs ??= await SharedPreferences.getInstance();
    await _prefs!.setString(_keyOfflineProfile, jsonString);
  }

  Future<String?> getCachedProfile() async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!.getString(_keyOfflineProfile);
  }

  Future<void> clearAll() async {
    await clearSessionToken();
    _prefs ??= await SharedPreferences.getInstance();
    await _prefs!.remove(_keyOfflineProfile);
    // Note: User's chosen language remains persisted per prompt:
    // "On logout: preference remains. On login: Hindi is restored."
  }
}
