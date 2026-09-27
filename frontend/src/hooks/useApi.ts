import { useState, useCallback, useEffect } from 'react';
import { ApiError } from '../services/apiClient';

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  execute: (...args: any[]) => Promise<T>;
  clear: () => void;
}

/**
 * A hook to wrap API calls with loading and error states.
 * @param apiFunc The API function to execute
 * @param immediate Whether to execute immediately on mount
 * @param initialArgs Arguments to pass if executing immediately
 */
export function useApi<T, Args extends any[] = any[]>(
  apiFunc: (...args: Args) => Promise<T>,
  immediate = false,
  initialArgs?: Args
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(immediate);
  const [error, setError] = useState<ApiError | null>(null);

  const execute = useCallback(
    async (...args: Args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiFunc(...args);
        setData(result);
        return result;
      } catch (err) {
        const apiError = err instanceof ApiError ? err : new ApiError(String(err));
        setError(apiError);
        throw apiError;
      } finally {
        setLoading(false);
      }
    },
    [apiFunc]
  );

  const clear = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (immediate && initialArgs) {
      execute(...initialArgs).catch(() => {});
    }
  }, [immediate, execute, JSON.stringify(initialArgs)]);

  return { data, loading, error, execute, clear };
}
