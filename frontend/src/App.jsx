/**
 * Root Application Component
 * ==========================
 *
 * Configures all Context Providers (Theme, Sidebar, Auth, Toast)
 * and defines the React Router routing tree with Public and Private Route guards.
 */
import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Providers
import { ThemeProvider } from './context/ThemeContext';
import { SidebarProvider } from './context/SidebarContext';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

// Guards
import PrivateRoute from './components/routing/PrivateRoute';
import PublicRoute from './components/routing/PublicRoute';
import RoleRoute from './components/routing/RoleRoute';

// Layout
import AppLayout from './components/layout/AppLayout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import PlantLibrary from './pages/PlantLibrary';
import PlantDetail from './pages/PlantDetail';
import PlantDetection from './pages/PlantDetection';
import RAGAssistant from './pages/RAGAssistant';
import ResearchPapers from './pages/ResearchPapers';
import Comparison from './pages/Comparison';
import History from './pages/History';
import Favorites from './pages/Favorites';
import Settings from './pages/Settings';
import ControlTower from './pages/ControlTower';
import About from './pages/About';
import NotFound from './pages/NotFound';

import { ROUTES } from './utils/routes';

export function App() {
  return (
    <ThemeProvider>
      <SidebarProvider>
        <AuthProvider>
          <ToastProvider>
            <Routes>
              {/* Public Routes Guard (Redirects to / if logged in) */}
              <Route element={<PublicRoute />}>
                <Route path={ROUTES.LOGIN} element={<Login />} />
                <Route path={ROUTES.REGISTER} element={<Register />} />
              </Route>

              {/* Private Routes Guard (Redirects to /login if logged out) */}
              <Route element={<PrivateRoute />}>
                {/* Main App Layout */}
                <Route element={<AppLayout />}>
                  <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
                  <Route path="/plants" element={<PlantLibrary />} />
                  <Route path="/plants/:id" element={<PlantDetail />} />
                  <Route path={ROUTES.PLANT_DETECTION} element={<PlantDetection />} />
                  <Route path={ROUTES.RAG_ASSISTANT} element={<RAGAssistant />} />
                  <Route path={ROUTES.COMPARISON} element={<Comparison />} />
                  <Route path={ROUTES.HISTORY} element={<History />} />
                  <Route path={ROUTES.FAVORITES} element={<Favorites />} />
                  <Route path={ROUTES.SETTINGS} element={<Settings />} />
                  <Route path={ROUTES.ABOUT} element={<About />} />
                  <Route path={ROUTES.RESEARCH_PAPERS} element={<ResearchPapers />} />
                  {/* Developer-only routes */}
                  <Route element={<RoleRoute requiredRole="developer" />}>
                    <Route path={ROUTES.CONTROL_TOWER} element={<ControlTower />} />
                  </Route>
                  <Route path={ROUTES.NOT_FOUND} element={<NotFound />} />
                </Route>
              </Route>
            </Routes>
          </ToastProvider>
        </AuthProvider>
      </SidebarProvider>
    </ThemeProvider>
  );
}

export default App;
