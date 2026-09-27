class AuthResponseModel {
  final bool authenticated;
  final String? userId;
  final String? citizenId;
  final String? name;
  final String? email;
  final String? phone;
  final String role;
  final String preferredLanguage;
  final bool onboardingCompleted;
  final int onboardingStep;
  final String? sessionToken;
  final String? token;

  AuthResponseModel({
    required this.authenticated,
    this.userId,
    this.citizenId,
    this.name,
    this.email,
    this.phone,
    this.role = 'citizen',
    this.preferredLanguage = 'hi',
    this.onboardingCompleted = false,
    this.onboardingStep = 1,
    this.sessionToken,
    this.token,
  });

  String? get activeToken => sessionToken ?? token;

  factory AuthResponseModel.fromJson(Map<String, dynamic> json) {
    return AuthResponseModel(
      authenticated: json['authenticated'] ?? false,
      userId: json['user_id']?.toString(),
      citizenId: json['citizen_id']?.toString(),
      name: json['name']?.toString(),
      email: json['email']?.toString(),
      phone: json['phone']?.toString(),
      role: json['role']?.toString() ?? 'citizen',
      preferredLanguage: json['preferred_language']?.toString() ?? 'hi',
      onboardingCompleted: json['onboarding_completed'] ?? false,
      onboardingStep: json['onboarding_step'] is int ? json['onboarding_step'] : 1,
      sessionToken: json['session_token']?.toString(),
      token: json['token']?.toString(),
    );
  }
}

class CitizenProfileModel {
  final String id;
  final String userId;
  final String? name;
  final String? dateOfBirth;
  final String? gender;
  final String? casteCategory;
  final String? currentState;
  final String? currentDistrict;
  final String? permanentState;
  final String? permanentDistrict;
  final bool isMigrant;
  final String? occupation;
  final String? occupationSector;
  final double? incomeMonthly;
  final bool hasDisability;
  final bool onboardingCompleted;
  final int onboardingStep;
  final String preferredLanguage;

  CitizenProfileModel({
    required this.id,
    required this.userId,
    this.name,
    this.dateOfBirth,
    this.gender,
    this.casteCategory,
    this.currentState,
    this.currentDistrict,
    this.permanentState,
    this.permanentDistrict,
    this.isMigrant = false,
    this.occupation,
    this.occupationSector,
    this.incomeMonthly,
    this.hasDisability = false,
    this.onboardingCompleted = false,
    this.onboardingStep = 1,
    this.preferredLanguage = 'hi',
  });

  factory CitizenProfileModel.fromJson(Map<String, dynamic> json) {
    return CitizenProfileModel(
      id: json['id']?.toString() ?? '',
      userId: json['user_id']?.toString() ?? '',
      name: json['name']?.toString(),
      dateOfBirth: json['date_of_birth']?.toString(),
      gender: json['gender']?.toString(),
      casteCategory: json['caste_category']?.toString(),
      currentState: json['current_state']?.toString(),
      currentDistrict: json['current_district']?.toString(),
      permanentState: json['permanent_state']?.toString(),
      permanentDistrict: json['permanent_district']?.toString(),
      isMigrant: json['is_migrant'] ?? false,
      occupation: json['occupation']?.toString(),
      occupationSector: json['occupation_sector']?.toString(),
      incomeMonthly: json['income_monthly'] != null
          ? double.tryParse(json['income_monthly'].toString())
          : null,
      hasDisability: json['has_disability'] ?? false,
      onboardingCompleted: json['onboarding_completed'] ?? false,
      onboardingStep: json['onboarding_step'] is int ? json['onboarding_step'] : 1,
      preferredLanguage: json['preferred_language']?.toString() ?? 'hi',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'name': name,
      'date_of_birth': dateOfBirth,
      'gender': gender,
      'caste_category': casteCategory,
      'current_state': currentState,
      'current_district': currentDistrict,
      'permanent_state': permanentState,
      'permanent_district': permanentDistrict,
      'is_migrant': isMigrant,
      'occupation': occupation,
      'occupation_sector': occupationSector,
      'income_monthly': incomeMonthly,
      'has_disability': hasDisability,
      'onboarding_completed': onboardingCompleted,
      'onboarding_step': onboardingStep,
      'preferred_language': preferredLanguage,
    };
  }
}

class SchemeBenefitModel {
  final String id;
  final String code;
  final String name;
  final String? nameHi;
  final String? ministry;
  final String? description;
  final String? descriptionHi;
  final String? benefitType;
  final double? monthlyValue;
  final String? targetGroup;
  final String status;
  final double readinessScore;
  final List<String> matchReasons;
  final List<String> unmetRules;
  final List<String> requiredDocuments;
  final String? policyVersion;
  final String? provenance;
  final String? officialUrl;

  SchemeBenefitModel({
    required this.id,
    required this.code,
    required this.name,
    this.nameHi,
    this.ministry,
    this.description,
    this.descriptionHi,
    this.benefitType,
    this.monthlyValue,
    this.targetGroup,
    this.status = 'eligible',
    this.readinessScore = 0.0,
    this.matchReasons = const [],
    this.unmetRules = const [],
    this.requiredDocuments = const [],
    this.policyVersion,
    this.provenance,
    this.officialUrl,
  });

  String localizedName(String lang) {
    if (lang == 'hi' && nameHi != null && nameHi!.isNotEmpty) {
      return nameHi!;
    }
    return name;
  }

  String localizedDescription(String lang) {
    if (lang == 'hi' && descriptionHi != null && descriptionHi!.isNotEmpty) {
      return descriptionHi!;
    }
    return description ?? '';
  }

  factory SchemeBenefitModel.fromJson(Map<String, dynamic> json) {
    final rawMatches = json['match_reasons'] ?? json['matched_rules'] ?? [];
    final matchReasons = rawMatches is List
        ? rawMatches.map((e) => e.toString()).toList()
        : <String>[];

    final rawUnmet = json['unmet_rules'] ?? json['missing_requirements'] ?? [];
    final unmetRules = rawUnmet is List
        ? rawUnmet.map((e) => e.toString()).toList()
        : <String>[];

    final rawDocs = json['required_documents'] ?? [];
    final requiredDocuments = rawDocs is List
        ? rawDocs.map((e) => e.toString()).toList()
        : <String>[];

    return SchemeBenefitModel(
      id: json['id']?.toString() ?? '',
      code: json['code']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      nameHi: json['name_hi']?.toString(),
      ministry: json['ministry']?.toString(),
      description: json['description']?.toString(),
      descriptionHi: json['description_hi']?.toString(),
      benefitType: json['benefit_type']?.toString(),
      monthlyValue: json['monthly_value'] != null
          ? double.tryParse(json['monthly_value'].toString())
          : (json['amount'] != null ? double.tryParse(json['amount'].toString()) : null),
      targetGroup: json['target_group']?.toString(),
      status: json['status']?.toString() ?? (json['eligible'] == true ? 'eligible' : 'potentially_eligible'),
      readinessScore: json['readiness_score'] != null
          ? (double.tryParse(json['readiness_score'].toString()) ?? 0.0)
          : 0.0,
      matchReasons: matchReasons,
      unmetRules: unmetRules,
      requiredDocuments: requiredDocuments,
      policyVersion: json['policy_version']?.toString(),
      provenance: json['provenance']?.toString(),
      officialUrl: json['official_url']?.toString(),
    );
  }
}

class WelfareStateModel {
  final String? citizenId;
  final double totalPotentialMonthlyBenefit;
  final int eligibleSchemesCount;
  final int schemesReadyToApply;
  final double evidenceReadinessScore;
  final List<SchemeBenefitModel> activeSchemes;
  final List<String> recommendedActions;

  WelfareStateModel({
    this.citizenId,
    required this.totalPotentialMonthlyBenefit,
    required this.eligibleSchemesCount,
    required this.schemesReadyToApply,
    required this.evidenceReadinessScore,
    this.activeSchemes = const [],
    this.recommendedActions = const [],
  });

  factory WelfareStateModel.fromJson(Map<String, dynamic> json) {
    final schemesRaw = json['active_schemes'] ?? json['schemes'] ?? [];
    final schemesList = schemesRaw is List
        ? schemesRaw.map((s) => SchemeBenefitModel.fromJson(s as Map<String, dynamic>)).toList()
        : <SchemeBenefitModel>[];

    final actionsRaw = json['recommended_actions'] ?? [];
    final actionsList = actionsRaw is List
        ? actionsRaw.map((a) => a.toString()).toList()
        : <String>[];

    return WelfareStateModel(
      citizenId: json['citizen_id']?.toString(),
      totalPotentialMonthlyBenefit: json['total_potential_monthly_benefit'] != null
          ? (double.tryParse(json['total_potential_monthly_benefit'].toString()) ?? 0.0)
          : (json['monthly_entitlement'] != null
              ? (double.tryParse(json['monthly_entitlement'].toString()) ?? 0.0)
              : 0.0),
      eligibleSchemesCount: json['eligible_schemes_count'] is int
          ? json['eligible_schemes_count']
          : schemesList.length,
      schemesReadyToApply: json['schemes_ready_to_apply'] is int
          ? json['schemes_ready_to_apply']
          : 0,
      evidenceReadinessScore: json['evidence_readiness_score'] != null
          ? (double.tryParse(json['evidence_readiness_score'].toString()) ?? 0.0)
          : 0.0,
      activeSchemes: schemesList,
      recommendedActions: actionsList,
    );
  }
}

class DocumentItemModel {
  final String id;
  final String citizenId;
  final String title;
  final String documentType;
  final String? mimeType;
  final int fileSizeBytes;
  final String verificationStatus;
  final String? createdAt;
  final Map<String, dynamic>? extractedFields;

  DocumentItemModel({
    required this.id,
    required this.citizenId,
    required this.title,
    required this.documentType,
    this.mimeType,
    this.fileSizeBytes = 0,
    required this.verificationStatus,
    this.createdAt,
    this.extractedFields,
  });

  factory DocumentItemModel.fromJson(Map<String, dynamic> json) {
    return DocumentItemModel(
      id: json['id']?.toString() ?? '',
      citizenId: json['citizen_id']?.toString() ?? '',
      title: json['title']?.toString() ?? json['filename']?.toString() ?? 'Document',
      documentType: json['document_type']?.toString() ?? 'other',
      mimeType: json['mime_type']?.toString(),
      fileSizeBytes: json['file_size_bytes'] is int ? json['file_size_bytes'] : 0,
      verificationStatus: json['verification_status']?.toString() ?? 'pending',
      createdAt: json['created_at']?.toString(),
      extractedFields: json['extracted_fields'] is Map<String, dynamic>
          ? json['extracted_fields'] as Map<String, dynamic>
          : null,
    );
  }
}

class ApplicationItemModel {
  final String id;
  final String citizenId;
  final String schemeId;
  final String schemeName;
  final String? schemeCode;
  final String status;
  final String? appliedAt;
  final String? updatedAt;
  final String? referenceNumber;
  final List<String> timeline;

  ApplicationItemModel({
    required this.id,
    required this.citizenId,
    required this.schemeId,
    required this.schemeName,
    this.schemeCode,
    required this.status,
    this.appliedAt,
    this.updatedAt,
    this.referenceNumber,
    this.timeline = const [],
  });

  factory ApplicationItemModel.fromJson(Map<String, dynamic> json) {
    final rawTimeline = json['timeline'] ?? [];
    final timelineList = rawTimeline is List
        ? rawTimeline.map((e) => e.toString()).toList()
        : <String>[];

    return ApplicationItemModel(
      id: json['id']?.toString() ?? '',
      citizenId: json['citizen_id']?.toString() ?? '',
      schemeId: json['scheme_id']?.toString() ?? '',
      schemeName: json['scheme_name']?.toString() ?? json['scheme']?.toString() ?? 'Welfare Application',
      schemeCode: json['scheme_code']?.toString(),
      status: json['status']?.toString() ?? 'prepared',
      appliedAt: json['applied_at']?.toString() ?? json['created_at']?.toString(),
      updatedAt: json['updated_at']?.toString(),
      referenceNumber: json['reference_number']?.toString(),
      timeline: timelineList,
    );
  }
}
