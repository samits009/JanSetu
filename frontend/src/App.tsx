import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Benefits, BenefitDetail } from './pages/Benefits';
import { Documents, DocumentDetail } from './pages/Documents';
import { Applications } from './pages/Applications';
import { Profile } from './pages/Profile';
import { SurvivalMap } from './pages/SurvivalMap';
import { Login } from './pages/Login';
import { Onboarding } from './pages/Onboarding';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { I18nProvider } from './i18n/I18nContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AgentChat } from './components/AgentChat';

function AppRoutes() {
  const { user } = useAuth();

  return (
    <I18nProvider initialLanguage={user?.preferred_language}>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Login />} />
        <Route path="/forgot-password" element={<Login />} />

        {/* Protected Application Routes */}
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <Layout>
                <Onboarding />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Home />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/benefits"
          element={
            <ProtectedRoute>
              <Layout>
                <Benefits />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/benefits/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <BenefitDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <Layout>
                <Documents />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <DocumentDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/applications"
          element={
            <ProtectedRoute>
              <Layout>
                <Applications />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Layout>
                <Profile />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/survival"
          element={
            <ProtectedRoute>
              <Layout>
                <SurvivalMap />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/agent"
          element={
            <ProtectedRoute>
              <Layout>
                <AgentChat />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </I18nProvider>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
