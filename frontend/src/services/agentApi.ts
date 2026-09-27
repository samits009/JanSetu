import { apiClient } from './apiClient';
import { AgentChatResponse, ConsentRequestData } from '../domain/models';

export const agentApi = {
  chat: (citizenId: string, message: string) =>
    apiClient.post<AgentChatResponse>('/api/agent/chat', { citizen_id: citizenId, message }),
    
  // In the real system, you might have a specific consent grant endpoint, or it could be on the application router
  // For the demo, assuming we post to the agent router or application router
  grantConsent: (consentId: string, action: string, applicationId?: string) =>
    apiClient.post<any>(`/api/agent/consent/${consentId}/grant`, { action, application_id: applicationId })
};
