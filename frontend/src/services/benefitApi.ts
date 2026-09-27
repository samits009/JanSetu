import { apiClient } from './apiClient';
import { BenefitSummary, BenefitDetail } from '../domain/models';

export const benefitApi = {
  listBenefits: (citizenId: string) =>
    apiClient.get<BenefitSummary[]>(`/api/citizens/${citizenId}/benefits`),
    
  getBenefit: (benefitId: string, citizenId: string) =>
    apiClient.get<BenefitDetail>(`/api/benefits/${benefitId}?citizen_id=${citizenId}`)
};
