import { useEffect } from 'react';
import { useAuth } from '../auth/AuthContext';
import { useApi } from './useApi';
import { welfareApi } from '../services/welfareApi';
import { WelfareState } from '../domain/models';

export function useWelfareState() {
  const { currentCitizenId } = useAuth();
  
  const { data, loading, error, execute } = useApi<WelfareState, [string]>(
    welfareApi.getWelfareState,
    false // don't execute automatically without citizenId
  );

  useEffect(() => {
    if (currentCitizenId) {
      execute(currentCitizenId).catch(() => {});
    }
  }, [currentCitizenId, execute]);

  return { welfareState: data, loading, error, refetch: () => execute(currentCitizenId) };
}
