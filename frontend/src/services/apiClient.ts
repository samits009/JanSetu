export class ApiError extends Error {
  public code: string;
  public status: number;
  public retryable: boolean;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', status: number = 500, retryable: boolean = false) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.retryable = retryable;
  }
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 15000; // 15 seconds

interface FetchOptions extends RequestInit {
  timeout?: number;
}

async function fetchWithTimeout(url: string, options: FetchOptions = {}): Promise<Response> {
  const { timeout = DEFAULT_TIMEOUT, ...fetchOptions } = options;

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  const requestId = Math.random().toString(36).substring(2, 15);
  
  const headers = new Headers(fetchOptions.headers);
  headers.set('X-Request-ID', requestId);
  if (!(fetchOptions.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
      credentials: 'include',
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError('Request timed out', 'TIMEOUT_ERROR', 408, true);
    }
    throw new ApiError(error instanceof Error ? error.message : 'Network error', 'NETWORK_ERROR', 0, true);
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    if (response.status === 204) {
      return {} as T;
    }
    return response.json();
  }

  let errorData;
  try {
    errorData = await response.json();
  } catch {
    throw new ApiError(response.statusText, 'HTTP_ERROR', response.status, response.status >= 500);
  }

  throw new ApiError(
    errorData.message || response.statusText,
    errorData.error_code || 'HTTP_ERROR',
    response.status,
    errorData.retryable ?? response.status >= 500
  );
}

export const apiClient = {
  async get<T>(path: string, options?: FetchOptions): Promise<T> {
    const response = await fetchWithTimeout(`${BASE_URL}${path}`, {
      ...options,
      method: 'GET',
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, data?: any, options?: FetchOptions): Promise<T> {
    const response = await fetchWithTimeout(`${BASE_URL}${path}`, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
    return handleResponse<T>(response);
  },

  async postFormData<T>(path: string, data: FormData, options?: FetchOptions): Promise<T> {
    const response = await fetchWithTimeout(`${BASE_URL}${path}`, {
      ...options,
      method: 'POST',
      body: data,
    });
    return handleResponse<T>(response);
  },
  
  async put<T>(path: string, data?: any, options?: FetchOptions): Promise<T> {
    const response = await fetchWithTimeout(`${BASE_URL}${path}`, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
    return handleResponse<T>(response);
  },
  
  async delete<T>(path: string, options?: FetchOptions): Promise<T> {
    const response = await fetchWithTimeout(`${BASE_URL}${path}`, {
      ...options,
      method: 'DELETE',
    });
    return handleResponse<T>(response);
  }
};
