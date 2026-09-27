import { apiClient } from './apiClient';
import { ApplicationResponse, ApplicationDetail, RecoveryPlan } from '../domain/models';

export const applicationApi = {
  listApplications: (citizenId: string) =>
    apiClient.get<ApplicationResponse[]>(`/api/citizens/${citizenId}/applications`),
    
  createApplication: (citizenId: string, schemeId: string) =>
    apiClient.post<ApplicationResponse>('/api/applications/', { citizen_id: citizenId, scheme_id: schemeId }),
    
  getApplicationStatus: (applicationId: string) =>
    apiClient.get<ApplicationDetail>(`/api/applications/${applicationId}/status`),
    
  submitApplication: (applicationId: string) =>
    apiClient.post<ApplicationResponse>(`/api/applications/${applicationId}/submit`),
    
  listMyApplications: () =>
    apiClient.get<ApplicationResponse[]>('/api/applications/me'),

  getHandoff: (applicationId: string) =>
    apiClient.post<any>(`/api/applications/${applicationId}/handoff`),
    
  recoverApplication: (applicationId: string) =>
    apiClient.post<RecoveryPlan>(`/api/applications/${applicationId}/recover`),
    
  resubmitApplication: (applicationId: string) =>
    apiClient.post<ApplicationResponse>(`/api/applications/${applicationId}/resubmit`)
};
