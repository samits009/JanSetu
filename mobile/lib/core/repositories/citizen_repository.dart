import '../models/models.dart';
import '../networking/api_client.dart';

class CitizenRepository {
  final ApiClient _apiClient;

  CitizenRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<Map<String, dynamic>> getMyProfile() async {
    final response = await _apiClient.get('/api/citizens/me');
    if (response is Map<String, dynamic> && response.containsKey('profile')) {
      return response['profile'] as Map<String, dynamic>;
    }
    return response as Map<String, dynamic>;
  }

  Future<WelfareStateModel> getWelfareState([String? language]) async {
    final params = language != null ? {'language': language} : null;
    final response = await _apiClient.get(
      '/api/citizens/me/welfare-state',
      queryParameters: params,
    );
    return WelfareStateModel.fromJson(response as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> saveOnboardingStep({
    required int step,
    String? name,
    String? dob,
    String? gender,
    String? phone,
    String? currentState,
    String? currentDistrict,
    String? permanentState,
    String? permanentDistrict,
    String? occupation,
    String? employmentStatus,
    double? annualIncome,
    int? householdMembersCount,
    int? childrenCount,
  }) async {
    final body = <String, dynamic>{
      'step': step,
      if (name != null) 'name': name,
      if (dob != null) 'dob': dob,
      if (gender != null) 'gender': gender,
      if (phone != null) 'phone': phone,
      if (currentState != null) 'current_state': currentState,
      if (currentDistrict != null) 'current_district': currentDistrict,
      if (permanentState != null) 'permanent_state': permanentState,
      if (permanentDistrict != null) 'permanent_district': permanentDistrict,
      if (occupation != null) 'occupation': occupation,
      if (employmentStatus != null) 'employment_status': employmentStatus,
      if (annualIncome != null) 'annual_income': annualIncome,
      if (householdMembersCount != null) 'household_members_count': householdMembersCount,
      if (childrenCount != null) 'children_count': childrenCount,
    };

    final response = await _apiClient.post(
      '/api/citizens/me/onboarding/step',
      body: body,
    );
    return response as Map<String, dynamic>;
  }

  Future<void> completeOnboarding() async {
    await _apiClient.post('/api/citizens/me/onboarding/complete');
  }

  Future<List<SchemeBenefitModel>> getBenefits() async {
    final response = await _apiClient.get('/api/citizens/me/benefits');
    if (response is List) {
      return response
          .map((item) => SchemeBenefitModel.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  Future<Map<String, dynamic>> getBenefitWhyApply(String schemeId) async {
    final response = await _apiClient.get('/api/schemes/$schemeId/why-apply');
    return response as Map<String, dynamic>;
  }

  Future<List<DocumentItemModel>> getDocuments() async {
    final response = await _apiClient.get('/api/citizens/me/documents');
    if (response is List) {
      return response
          .map((item) => DocumentItemModel.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  Future<DocumentItemModel> uploadDocument({
    required String title,
    required String documentType,
    required List<int> fileBytes,
    required String fileName,
  }) async {
    final response = await _apiClient.uploadFile(
      '/api/documents',
      fieldName: 'file',
      fileBytes: fileBytes,
      fileName: fileName,
      extraFields: {
        'title': title,
        'document_type': documentType,
      },
    );
    return DocumentItemModel.fromJson(response as Map<String, dynamic>);
  }

  Future<List<ApplicationItemModel>> getApplications() async {
    final response = await _apiClient.get('/api/citizens/me/applications');
    if (response is List) {
      return response
          .map((item) => ApplicationItemModel.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  Future<Map<String, dynamic>> prepareApplication(String schemeId) async {
    final response = await _apiClient.post('/api/applications/prepare', body: {
      'scheme_id': schemeId,
    });
    return response as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> grantConsent({
    required String consentId,
    required String action,
    required String scope,
  }) async {
    final response = await _apiClient.post('/api/agent/consent/$consentId/grant', body: {
      'action': action,
      'scope': scope,
    });
    return response as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> relocateCitizen({
    required String newState,
    required String newDistrict,
  }) async {
    final response = await _apiClient.post('/api/survival/simulate', body: {
      'new_state': newState,
      'new_district': newDistrict,
    });
    return response as Map<String, dynamic>;
  }
}
