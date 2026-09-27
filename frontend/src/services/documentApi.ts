import { apiClient } from './apiClient';
import { DocumentDetailResponse, DocumentResponse, EvidenceResponse } from '../domain/models';

export const documentApi = {
  listDocuments: (citizenId: string) =>
    apiClient.get<DocumentResponse[]>(`/api/citizens/${citizenId}/documents`),
    
  listEvidence: (citizenId: string) =>
    apiClient.get<EvidenceResponse[]>(`/api/citizens/${citizenId}/evidence`),

  uploadDocument: (citizenId: string, documentType: string, file: File) => {
    const form = new FormData();
    form.append('citizen_id', citizenId);
    form.append('document_type', documentType);
    form.append('file', file);
    return apiClient.postFormData<DocumentUploadResponse>('/api/documents/', form);
  },

  getDocument: (citizenId: string, documentId: string) =>
    apiClient.get<DocumentDetailResponse>(`/api/documents/${documentId}?citizen_id=${citizenId}`)
};

export interface DocumentUploadResponse {
  document_id: string;
  status: string;
  document_type: string;
  uploaded_at: string;
  duplicate_detected: boolean;
}
