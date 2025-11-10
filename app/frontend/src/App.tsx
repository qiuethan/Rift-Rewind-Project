import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import LandingPage from '@/pages/LandingPage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import GamesPage from '@/pages/GamesPage';
import ChampionsPage from '@/pages/ChampionsPage';
import ChampionDetailPage from '@/pages/ChampionDetailPage';
import MatchDetailPage from '@/pages/MatchDetailPage';
import TestChatPage from '@/pages/TestChatPage';
import RecommendPage from '@/pages/RecommendPage';
import { Footer, ScrollToTop } from '@/components';
import { ROUTES, STORAGE_KEYS } from '@/config';
import { authActions } from '@/actions/auth';
import { SummonerProvider, ThemeProvider } from '@/contexts';
import { supabase } from '@/lib/supabase';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = authActions.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to={ROUTES.LOGIN} />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = authActions.isAuthenticated();
  return !isAuthenticated ? <>{children}</> : <Navigate to={ROUTES.DASHBOARD} />;
}

function App() {
  const [sessionChecked, setSessionChecked] = useState(false);

  // Verify session on app mount and listen for auth changes
  useEffect(() => {
    const verifySession = async () => {
      if (authActions.isAuthenticated()) {
        const result = await authActions.verifyToken();
        if (!result.success) {
          // Token expired, clear auth state
          console.log('Session expired, logging out');
          await authActions.logout();
        }
      }
      setSessionChecked(true);
    };

    verifySession();

    // Listen for auth state changes (token refresh, logout, etc.)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event);
      
      if (event === 'SIGNED_OUT' || event === 'TOKEN_REFRESHED') {
        if (session?.access_token) {
          // Update stored token on refresh
          localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, session.access_token);
        } else {
          // Clear on sign out
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.USER_DATA);
        }
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Show loading while checking session
  if (!sessionChecked) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <ScrollToTop />
      <ThemeProvider>
        <SummonerProvider>
          <Routes>
          <Route path={ROUTES.HOME} element={<LandingPage />} />
          <Route
            path={ROUTES.LOGIN}
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path={ROUTES.REGISTER}
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />
          <Route
            path={ROUTES.DASHBOARD}
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.GAMES}
            element={
              <ProtectedRoute>
                <GamesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.CHAMPIONS}
            element={
              <ProtectedRoute>
                <ChampionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.RECOMMEND}
            element={
              <ProtectedRoute>
                <RecommendPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/champion/:championName"
            element={
              <ProtectedRoute>
                <ChampionDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.MATCH}
            element={
              <ProtectedRoute>
                <MatchDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.TEST_CHAT}
            element={
              <ProtectedRoute>
                <TestChatPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to={ROUTES.HOME} />} />
          </Routes>
          <Footer />
        </SummonerProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
