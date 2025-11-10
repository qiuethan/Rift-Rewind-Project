import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState, ReactNode } from 'react';
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
import { AudioProvider } from '@/contexts/AudioContext'; // Import the new AudioProvider
import { supabase } from '@/lib/supabase';

// Define props for route components
interface RouteProps {
  children: ReactNode;
}

function ProtectedRoute({ children }: RouteProps) {
  const isAuthenticated = authActions.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to={ROUTES.LOGIN} />;
}

function PublicRoute({ children }: RouteProps) {
  const isAuthenticated = authActions.isAuthenticated();
  return !isAuthenticated ? <>{children}</> : <Navigate to={ROUTES.DASHBOARD} />;
}

function App() {
  const [sessionChecked, setSessionChecked] = useState(false);

  useEffect(() => {
    const verifySession = async () => {
      if (authActions.isAuthenticated()) {
        const result = await authActions.verifyToken();
        if (!result.success) {
          console.log('Session expired, logging out');
          await authActions.logout();
        }
      }
      setSessionChecked(true);
    };

    verifySession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event);
      
      if (event === 'SIGNED_OUT' || event === 'TOKEN_REFRESHED') {
        if (session?.access_token) {
          localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, session.access_token);
        } else {
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.USER_DATA);
        }
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  if (!sessionChecked) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <AudioProvider audioSrc="/audio/midgame.mp3">
      <BrowserRouter>
        <ScrollToTop />
        <ThemeProvider>
          <SummonerProvider>
            <Routes>
              <Route path={ROUTES.HOME} element={<LandingPage />} />
              <Route path={ROUTES.LOGIN} element={<PublicRoute><LoginPage /></PublicRoute>} />
              <Route path={ROUTES.REGISTER} element={<PublicRoute><RegisterPage /></PublicRoute>} />
              <Route path={ROUTES.DASHBOARD} element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
              <Route path={ROUTES.GAMES} element={<ProtectedRoute><GamesPage /></ProtectedRoute>} />
              <Route path={ROUTES.CHAMPIONS} element={<ProtectedRoute><ChampionsPage /></ProtectedRoute>} />
              <Route path="/champion/:championName" element={<ProtectedRoute><ChampionDetailPage /></ProtectedRoute>} />
              <Route path={ROUTES.MATCH} element={<ProtectedRoute><MatchDetailPage /></ProtectedRoute>} />
              <Route path={ROUTES.TEST_CHAT} element={<ProtectedRoute><TestChatPage /></ProtectedRoute>} />
              <Route path="*" element={<Navigate to={ROUTES.HOME} />} />
            </Routes>
            <Footer />
          </SummonerProvider>
        </ThemeProvider>
      </BrowserRouter>
    </AudioProvider>
  );
}

export default App;