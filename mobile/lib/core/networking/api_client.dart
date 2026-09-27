import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../errors/api_exception.dart';
import '../storage/secure_storage.dart';

class ApiClient {
  final http.Client _httpClient;
  final StorageService _storageService;
  final String _baseUrl;

  ApiClient({
    http.Client? httpClient,
    required StorageService storageService,
    String? baseUrl,
  })  : _httpClient = httpClient ?? http.Client(),
        _storageService = storageService,
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  String get baseUrl => _baseUrl;

  Future<Map<String, String>> _buildHeaders({bool isMultipart = false}) async {
    final headers = <String, String>{
      'Accept': 'application/json',
    };
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }

    final token = await _storageService.getSessionToken();
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
      // Also send cookie for dual compatibility with FastAPI session cookie backend
      headers['Cookie'] = 'jansetu_session=$token';
    }

    final lang = await _storageService.getLanguage();
    headers['Accept-Language'] = lang;

    return headers;
  }

  Uri _buildUri(String path, [Map<String, dynamic>? queryParameters]) {
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    final fullUrl = '$_baseUrl$normalizedPath';
    final uri = Uri.parse(fullUrl);
    if (queryParameters != null && queryParameters.isNotEmpty) {
      final stringParams = queryParameters.map((k, v) => MapEntry(k, v.toString()));
      return uri.replace(queryParameters: stringParams);
    }
    return uri;
  }

  // --- GET ---
  Future<dynamic> get(String path, {Map<String, dynamic>? queryParameters}) async {
    final uri = _buildUri(path, queryParameters);
    try {
      final headers = await _buildHeaders();
      final response = await _httpClient
          .get(uri, headers: headers)
          .timeout(AppConfig.connectTimeout);
      return _processResponse(response);
    } on SocketException {
      throw ApiException.networkError();
    } on TimeoutException {
      throw ApiException.timeout();
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: e.toString());
    }
  }

  // --- POST ---
  Future<dynamic> post(String path, {dynamic body}) async {
    final uri = _buildUri(path);
    try {
      final headers = await _buildHeaders();
      final encodedBody = body != null ? jsonEncode(body) : null;
      final response = await _httpClient
          .post(uri, headers: headers, body: encodedBody)
          .timeout(AppConfig.connectTimeout);
      return _processResponse(response);
    } on SocketException {
      throw ApiException.networkError();
    } on TimeoutException {
      throw ApiException.timeout();
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: e.toString());
    }
  }

  // --- PUT ---
  Future<dynamic> put(String path, {dynamic body}) async {
    final uri = _buildUri(path);
    try {
      final headers = await _buildHeaders();
      final encodedBody = body != null ? jsonEncode(body) : null;
      final response = await _httpClient
          .put(uri, headers: headers, body: encodedBody)
          .timeout(AppConfig.connectTimeout);
      return _processResponse(response);
    } on SocketException {
      throw ApiException.networkError();
    } on TimeoutException {
      throw ApiException.timeout();
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: e.toString());
    }
  }

  // --- PATCH ---
  Future<dynamic> patch(String path, {dynamic body}) async {
    final uri = _buildUri(path);
    try {
      final headers = await _buildHeaders();
      final encodedBody = body != null ? jsonEncode(body) : null;
      final response = await _httpClient
          .patch(uri, headers: headers, body: encodedBody)
          .timeout(AppConfig.connectTimeout);
      return _processResponse(response);
    } on SocketException {
      throw ApiException.networkError();
    } on TimeoutException {
      throw ApiException.timeout();
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: e.toString());
    }
  }

  // --- DELETE ---
  Future<dynamic> delete(String path) async {
    final uri = _buildUri(path);
    try {
      final headers = await _buildHeaders();
      final response = await _httpClient
          .delete(uri, headers: headers)
          .timeout(AppConfig.connectTimeout);
      return _processResponse(response);
    } on SocketException {
      throw ApiException.networkError();
    } on TimeoutException {
      throw ApiException.timeout();
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: e.toString());
    }
  }

  // --- MULTIPART UPLOAD (Camera / Document / Gallery) ---
  Future<dynamic> uploadFile(
    String path, {
    required String fieldName,
    required List<int> fileBytes,
    required String fileName,
    Map<String, String>? extraFields,
  }) async {
    final uri = _buildUri(path);
    try {
      final request = http.MultipartRequest('POST', uri);
      final headers = await _buildHeaders(isMultipart: true);
      request.headers.addAll(headers);

      if (extraFields != null) {
        request.fields.addAll(extraFields);
      }

      final multipartFile = http.MultipartFile.fromBytes(
        fieldName,
        fileBytes,
        filename: fileName,
      );
      request.files.add(multipartFile);

      final streamedResponse = await request.send().timeout(AppConfig.receiveTimeout);
      final response = await http.Response.fromStream(streamedResponse);
      return _processResponse(response);
    } on SocketException {
      throw ApiException.networkError();
    } on TimeoutException {
      throw ApiException.timeout();
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: e.toString());
    }
  }

  dynamic _processResponse(http.Response response) {
    dynamic responseBody;
    try {
      if (response.body.isNotEmpty) {
        responseBody = jsonDecode(utf8.decode(response.bodyBytes));
      }
    } catch (_) {
      responseBody = response.body;
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return responseBody;
    }

    String? detail;
    if (responseBody is Map && responseBody.containsKey('detail')) {
      final d = responseBody['detail'];
      if (d is String) {
        detail = d;
      } else if (d is List && d.isNotEmpty && d[0] is Map && d[0].containsKey('msg')) {
        detail = d[0]['msg'] as String;
      } else {
        detail = d.toString();
      }
    }

    throw ApiException.fromStatusCode(
      response.statusCode,
      detail: detail,
      raw: responseBody,
    );
  }
}
