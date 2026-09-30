/**
 * Root Application Component
 * ==========================
 *
 * Configures all Context Providers (Theme, Sidebar, Toast)
 * and defines the React Router routing tree.
 */
import { Routes, Route } from 'react-router-dom';

// Providers
import { ThemeProvider } from './context/ThemeContext';
import { SidebarProvider } from './context/SidebarContext';
import { ToastProvider } from './context/ToastContext';

// Layout
import AppLayout from './components/layout/AppLayout';
import ErrorBoundary from './components/common/ErrorBoundary';

// Pages
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
        <ToastProvider>
          <ErrorBoundary>
            <Routes>
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
                <Route path={ROUTES.CONTROL_TOWER} element={<ControlTower />} />
                <Route path={ROUTES.NOT_FOUND} element={<NotFound />} />
              </Route>
            </Routes>
          </ErrorBoundary>
        </ToastProvider>
      </SidebarProvider>
    </ThemeProvider>
  );
}

export default App;
