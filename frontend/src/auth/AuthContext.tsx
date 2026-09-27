import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { apiClient } from '../services/apiClient';

export interface UserProfile {
  user_id: string;
  identity_id?: string;
  email?: string;
  phone?: string;
  mobile_number?: string;
  citizen_id: string;
  citizen_name?: string;
  name?: string;
  preferred_language: 'en' | 'hi';
  is_active?: boolean;
  email_verified?: boolean;
  mobile_verified?: boolean;
  requires_mobile?: boolean;
  google_linked?: boolean;
  onboarding_completed?: boolean;
  onboarding_step?: number;
}

export interface RegisterPayload {
  name: string;
  email: string;
  mobile_number: string;
  phone?: string;
  password: string;
  confirm_password?: string;
  preferred_language?: 'en' | 'hi';
}

interface AuthContextType {
  user: UserProfile | null;
  currentCitizenId: string;
  isAuthenticated: boolean;
  loading: boolean;
  login: (identifier: string, password: string) => Promise<UserProfile>;
  register: (payload: RegisterPayload) => Promise<UserProfile>;
  linkGoogle: (email: string, password: string, pendingSub: string) => Promise<UserProfile>;
  continueWithGoogle: () => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<UserProfile | null>;
  isDemoMode: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = useCallback(async (): Promise<UserProfile | null> => {
    try {
      const data = await apiClient.get<UserProfile>('/api/auth/me');
      // Normalize name from citizen_name
      if (data && !data.name && data.citizen_name) {
        data.name = data.citizen_name;
      }
      setUser(data);
      return data;
    } catch {
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchCurrentUser().finally(() => setLoading(false));
  }, [fetchCurrentUser]);

  const login = async (identifier: string, password: string): Promise<UserProfile> => {
    // Authenticate against PostgreSQL backend — supports email or mobile number
    const res = await apiClient.post<any>('/api/auth/login', {
      username: identifier,
      email: identifier,
      mobile_number: identifier,
      password,
    });
    if (res?.token || res?.session_token) {
      localStorage.setItem('jansetu_token', res.token || res.session_token);
    }
    if (res && res.authenticated) {
      if (!res.name && res.citizen_name) {
        res.name = res.citizen_name;
      }
      setUser(res);
      return res;
    }
    const profile = await fetchCurrentUser();
    if (!profile) {
      throw new Error('Failed to retrieve user session after login.');
    }
    return profile;
  };

  const register = async (payload: RegisterPayload): Promise<UserProfile> => {
    const res = await apiClient.post<any>('/api/auth/register', {
      ...payload,
      phone: payload.mobile_number || payload.phone,
    });
    if (res?.token || res?.session_token) {
      localStorage.setItem('jansetu_token', res.token || res.session_token);
    }
    if (res && res.authenticated) {
      if (!res.name && res.citizen_name) {
        res.name = res.citizen_name;
      }
      setUser(res);
      return res;
    }
    const profile = await fetchCurrentUser();
    if (!profile) {
      throw new Error('Failed to retrieve user session after registration.');
    }
    return profile;
  };

  const linkGoogle = async (email: string, password: string, pendingSub: string): Promise<UserProfile> => {
    const res = await apiClient.post<any>('/api/auth/link-google', {
      email,
      password,
      pending_sub: pendingSub,
    });
    if (res?.token || res?.session_token) {
      localStorage.setItem('jansetu_token', res.token || res.session_token);
    }
    const profile = await fetchCurrentUser();
    if (!profile) {
      throw new Error('Failed to retrieve user session after linking Google account.');
    }
    return profile;
  };

  const continueWithGoogle = () => {
    // Real Authorization Code redirect flow to Google Sign-In
    window.location.href = `${BASE_URL}/api/auth/google/login`;
  };

  const logout = async () => {
    try {
      await apiClient.post('/api/auth/logout');
    } catch {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('jansetu_token');
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    currentCitizenId: user?.citizen_id || '',
    isAuthenticated: !!user,
    loading,
    login,
    register,
    linkGoogle,
    continueWithGoogle,
    logout,
    refreshUser: fetchCurrentUser,
    isDemoMode: false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
