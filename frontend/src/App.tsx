import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from '@/pages/LandingPage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import { ROUTES } from '@/config';
import { authActions } from '@/actions/auth';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = authActions.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to={ROUTES.LOGIN} />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = authActions.isAuthenticated();
  return !isAuthenticated ? <>{children}</> : <Navigate to={ROUTES.DASHBOARD} />;
}

function App() {
  return (
    <BrowserRouter>
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
        <Route path="*" element={<Navigate to={ROUTES.HOME} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
