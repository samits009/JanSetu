import '../networking/api_client.dart';

class AgentExecutionStep {
  final String stepName;
  final String status;
  final String? details;

  AgentExecutionStep({
    required this.stepName,
    required this.status,
    this.details,
  });

  factory AgentExecutionStep.fromJson(Map<String, dynamic> json) {
    return AgentExecutionStep(
      stepName: json['tool']?.toString() ?? json['step']?.toString() ?? json['name']?.toString() ?? 'Operation',
      status: json['status']?.toString() ?? 'completed',
      details: json['summary']?.toString() ?? json['output']?.toString(),
    );
  }
}

class AgentChatResponse {
  final String message;
  final List<String> actions;
  final bool requiresConsent;
  final String? consentId;
  final String? consentAction;
  final String? consentApplicationId;
  final String? workflowState;
  final List<AgentExecutionStep> executionTrace;

  AgentChatResponse({
    required this.message,
    this.actions = const [],
    this.requiresConsent = false,
    this.consentId,
    this.consentAction,
    this.consentApplicationId,
    this.workflowState,
    this.executionTrace = const [],
  });

  factory AgentChatResponse.fromJson(Map<String, dynamic> json) {
    final rawActions = json['actions'] ?? [];
    final actionsList = rawActions is List
        ? rawActions.map((a) => a.toString()).toList()
        : <String>[];

    final rawTrace = json['execution_trace'] ?? [];
    final traceList = rawTrace is List
        ? rawTrace
            .map((t) => AgentExecutionStep.fromJson(t as Map<String, dynamic>))
            .toList()
        : <AgentExecutionStep>[];

    return AgentChatResponse(
      message: json['message']?.toString() ?? '',
      actions: actionsList,
      requiresConsent: json['requires_consent'] ?? false,
      consentId: json['consent_id']?.toString(),
      consentAction: json['consent_action']?.toString(),
      consentApplicationId: json['consent_application_id']?.toString(),
      workflowState: json['workflow_state']?.toString(),
      executionTrace: traceList,
    );
  }
}

class AgentRepository {
  final ApiClient _apiClient;

  AgentRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<AgentChatResponse> sendMessage(String message) async {
    final response = await _apiClient.post(
      '/api/agent/chat',
      body: {'message': message},
    );
    return AgentChatResponse.fromJson(response as Map<String, dynamic>);
  }
}
