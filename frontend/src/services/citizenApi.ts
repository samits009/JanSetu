import { apiClient } from './apiClient';
import { CitizenProfile } from '../domain/models';

export const citizenApi = {
  getCitizen: (citizenId: string) => 
    apiClient.get<CitizenProfile>(`/api/citizens/${citizenId}`)
};
