import { apiClient } from './apiClient';
import { WelfareState, SurvivalResult } from '../domain/models';

export const welfareApi = {
  getWelfareState: (citizenId: string) =>
    apiClient.get<WelfareState>(`/api/citizens/${citizenId}/welfare-state`),
    
  simulateLocationChange: (citizenId: string, newLocation: { state: string; district: string }) =>
    apiClient.post<SurvivalResult>(`/api/citizens/${citizenId}/location-change`, newLocation)
};
