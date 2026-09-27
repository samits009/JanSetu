import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { apiClient, ApiError } from '../services/apiClient';

export interface UserProfile {
  user_id: string;
  email: string;
  phone?: string;
  citizen_id: string;
  preferred_language: 'en' | 'hi';
  is_active: boolean;
  name?: string;
  onboarding_completed?: boolean;
}

export interface RegisterPayload {
  email: string;
  password: string;
  phone?: string;
  name?: string;
  preferred_language?: 'en' | 'hi';
  onboarding_completed?: boolean;
  onboarding_step?: number;
}

interface AuthContextType {
  user: UserProfile | null;
  currentCitizenId: string;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<UserProfile | null>;
  isDemoMode: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = useCallback(async (): Promise<UserProfile | null> => {
    try {
      const data = await apiClient.get<UserProfile>('/api/auth/me');
      setUser(data);
      return data;
    } catch (err) {
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchCurrentUser().finally(() => setLoading(false));
  }, [fetchCurrentUser]);

  const login = async (email: string, password: string) => {
    // Always authenticate against the real backend — no client-side fallbacks.
    await apiClient.post('/api/auth/login', { email, password, username: email });
    await fetchCurrentUser();
  };

  const register = async (payload: RegisterPayload) => {
    await apiClient.post('/api/auth/register', payload);
    await fetchCurrentUser();
  };

  const logout = async () => {
    try {
      await apiClient.post('/api/auth/logout');
    } catch {
      // Ignore network errors on logout
    } finally {
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
