import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import en from './en.json';
import hi from './hi.json';
import { apiClient } from '../services/apiClient';

export type Language = 'en' | 'hi';

const dictionaries: Record<Language, any> = {
  en,
  hi,
};

interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => Promise<boolean>;
  syncError: string | null;
  clearSyncError: () => void;
  isSyncing: boolean;
  t: (path: string, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({ children, initialLanguage }: { children: React.ReactNode; initialLanguage?: Language }) {
  const [language, setLanguageState] = useState<Language>(() => {
    // initialLanguage comes from the authenticated user's PostgreSQL record.
    // localStorage is a read-cache for the first render only.
    if (initialLanguage) return initialLanguage;
    const saved = localStorage.getItem('jansetu_language');
    if (saved === 'en' || saved === 'hi') return saved;
    return 'hi'; // Default to Hindi for India-first accessibility
  });
  const [syncError, setSyncError] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const clearSyncError = useCallback(() => setSyncError(null), []);

  const setLanguage = useCallback(async (lang: Language): Promise<boolean> => {
    // Optimistically update UI so citizen gets immediate feedback
    setLanguageState(lang);
    localStorage.setItem('jansetu_language', lang);
    document.documentElement.lang = lang;
    setIsSyncing(true);
    setSyncError(null);

    try {
      await apiClient.put('/api/citizens/me/preferences', { preferred_language: lang });
      setIsSyncing(false);
      return true;
    } catch (err: any) {
      setIsSyncing(false);
      const msg = lang === 'hi'
        ? 'भाषा प्राथमिकता सर्वर पर सुरक्षित नहीं हो सकी। कृपया पुनः प्रयास करें।'
        : 'Failed to persist language preference to server. Please retry.';
      setSyncError(msg);
      return false;
    }
  }, []);

  // Sync from parent (AuthContext passes the DB-loaded language on auth changes)
  useEffect(() => {
    if (initialLanguage && (initialLanguage === 'en' || initialLanguage === 'hi')) {
      setLanguageState(initialLanguage);
      localStorage.setItem('jansetu_language', initialLanguage);
      document.documentElement.lang = initialLanguage;
    }
  }, [initialLanguage]);

  const t = useCallback((path: string, fallback?: string): string => {
    const keys = path.split('.');
    let current = dictionaries[language];
    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key];
      } else {
        // Fallback to English if missing in Hindi
        let fallbackVal = dictionaries['en'];
        for (const fbKey of keys) {
          if (fallbackVal && typeof fallbackVal === 'object' && fbKey in fallbackVal) {
            fallbackVal = fallbackVal[fbKey];
          } else {
            return fallback || path;
          }
        }
        return typeof fallbackVal === 'string' ? fallbackVal : fallback || path;
      }
    }
    return typeof current === 'string' ? current : fallback || path;
  }, [language]);

  return (
    <I18nContext.Provider value={{ language, setLanguage, syncError, clearSyncError, isSyncing, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n(): I18nContextType {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return ctx;
}

