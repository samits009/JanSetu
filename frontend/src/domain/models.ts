export type BenefitStatus = 'ACTIVE' | 'AT_RISK' | 'EXPIRED' | 'PENDING' | 'INACTIVE';
export type ApplicationStatus = 'DISCOVERED' | 'ELIGIBILITY_CHECKED' | 'EVIDENCE_REQUIRED' | 'EVIDENCE_COMPLETE' | 'DRAFTED' | 'AWAITING_CONSENT' | 'SUBMITTING' | 'SUBMITTED' | 'UNDER_REVIEW' | 'REQUIRES_EVIDENCE' | 'REJECTED' | 'RECOVERY_READY' | 'RESUBMITTED' | 'APPROVED';
export type ConsentAction = 'APPLICATION_SUBMISSION' | 'APPLICATION_RESUBMISSION' | 'DATA_ACCESS';

// ---------------------------------------------------------
// Citizen Profile
// ---------------------------------------------------------

export interface Location {
  state: string;
  district: string;
  is_active: boolean;
  location_type: string;
}

export interface Employment {
  occupation: string;
  is_active: boolean;
  employer_name?: string;
}

export interface CitizenProfile {
  id: string;
  name: string;
  dob?: string;
  locations: Location[];
  employments: Employment[];
}

// ---------------------------------------------------------
// Welfare State
// ---------------------------------------------------------

export interface BenefitSummary {
  id: string;
  scheme_id: string;
  scheme_name: string;
  status: BenefitStatus;
  amount?: number;
}

export interface NewOpportunity {
  id: string;
  scheme_name: string;
  category: string;
  amount?: number;
  why_it_applies?: string[];
  matched_rules?: string[];
  missing_evidence?: string[];
  readiness_percentage?: number;
  verification_status?: string;
}

export interface ActionRequired {
  benefit_id?: string;
  application_id?: string;
  title: string;
  description: string;
  action_type: 'RENEWAL' | 'EVIDENCE_REQUIRED' | 'CONSENT_REQUIRED' | 'RECOVERY';
  urgency: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface RecommendedAction {
  title: string;
  description: string;
}

export interface WelfareState {
  active_benefits: BenefitSummary[];
  action_required: ActionRequired[];
  new_opportunities: NewOpportunity[];
  at_risk: BenefitSummary[];
  needs_verification: any[]; // Assuming generic for now
  pending_applications: any[];
  document_gaps: string[];
  recommended_actions: RecommendedAction[];
  citizen_summary: any;
  evidence_readiness_score?: number;
}


// ---------------------------------------------------------
// Benefits
// ---------------------------------------------------------

export interface RequirementEvaluation {
  id: string;
  name: string;
  type: string;
  is_satisfied: boolean;
  linked_evidence_id?: string;
  reason?: string;
}

export interface EvidenceDetail {
  id: string;
  type: string;
  document_type: string;
  confidence: string;
}

export interface BenefitDetail {
  id: string;
  scheme_id: string;
  scheme_name: string;
  status: BenefitStatus;
  eligibility_status: 'ELIGIBLE' | 'INELIGIBLE' | 'UNKNOWN';
  satisfied_requirements: RequirementEvaluation[];
  missing_requirements: RequirementEvaluation[];
  supporting_evidence: EvidenceDetail[];
  reasons: string[];
  application_status?: ApplicationStatus;
  application_id?: string;
}

// ---------------------------------------------------------
// Survival Map
// ---------------------------------------------------------

export interface SurvivalResult {
  continued_benefits: BenefitSummary[];
  changed_benefits: BenefitSummary[];
  new_benefits: NewOpportunity[];
  at_risk_benefits: BenefitSummary[];
  required_actions: ActionRequired[];
}

// ---------------------------------------------------------
// Documents
// ---------------------------------------------------------

export interface DocumentResponse {
  id: string;
  document_type: string;
  document_number: string;
  verification_status: string;
  extracted_data: Record<string, any>;
  status: string;
  uploaded_at?: string;
  processed_at?: string;
}

export interface DocumentDetailResponse extends DocumentResponse {
  storage_reference?: string;
  content_hash?: string;
  expires_at?: string;
  metadata: Record<string, any>;
  extraction_method?: string;
  processing_provider?: string;
  processing_model?: string;
  prompt_version?: string;
  evidence: EvidenceResponse[];
}

export interface EvidenceResponse {
  id: string;
  document_id: string;
  evidence_type: string;
  data: Record<string, any>;
  confidence: string;
  verification_status?: string;
  provenance?: Record<string, any>;
}

// ---------------------------------------------------------
// Applications
// ---------------------------------------------------------

export interface ApplicationRequirement {
  id: string;
  requirement_type: string;
  description: string;
  is_mandatory: boolean;
}

export interface ApplicationResponse {
  id: string;
  scheme_id: string;
  scheme_name: string;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetail {
  id: string;
  scheme_id: string;
  scheme_name: string;
  status: ApplicationStatus;
  requirements: ApplicationRequirement[];
  rejection_reason?: string;
  government_reference_id?: string;
  timeline: {
    status: ApplicationStatus;
    timestamp: string;
  }[];
}

export interface RecoveryPlan {
  application_id: string;
  original_rejection_reason: string;
  missing_requirements: ApplicationRequirement[];
  suggested_evidence: EvidenceResponse[];
  can_recover: boolean;
}

// ---------------------------------------------------------
// Agent & Consent
// ---------------------------------------------------------

export interface ExecutionTrace {
  timestamp: string;
  tool: string;
  purpose: string;
  status: string;
  safe_input_summary: Record<string, any>;
  safe_result_summary: Record<string, any>;
  duration_ms: number;
  consent_state: string;
}

export interface AgentChatResponse {
  message: string;
  actions: string[];
  requires_consent: boolean;
  consent_id?: string;
  consent_action?: ConsentAction;
  consent_application_id?: string;
  workflow_state?: string;
  execution_trace: ExecutionTrace[];
}

export interface ConsentRequestData {
  id: string;
  action: ConsentAction;
  application_id?: string;
  purpose: string;
  data_accessed: string[];
  destination: string;
  status: 'PENDING' | 'GRANTED' | 'DENIED' | 'EXPIRED';
}
