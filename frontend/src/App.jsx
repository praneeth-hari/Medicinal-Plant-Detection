/**
 * Root application component.
 *
 * Sets up React Router <Routes> and wraps the page tree with
 * global context providers (Auth, Theme).
 */
import { Routes, Route } from 'react-router-dom';

// -- Page imports (uncomment as pages are implemented) -----
// import Home from './pages/Home';
// import Detect from './pages/Detect';
// import Chat from './pages/Chat';
// import PlantLibrary from './pages/PlantLibrary';
// import PlantDetail from './pages/PlantDetail';
// import Login from './pages/Login';
// import Register from './pages/Register';
// import NotFound from './pages/NotFound';

// -- Layout import -----------------------------------------
// import Layout from './components/layout/Layout';

/**
 * App — top-level component rendered inside BrowserRouter.
 * @returns {JSX.Element}
 */
export function App() {
  return (
    <div className="min-h-screen bg-background-light text-surface-900 dark:bg-background-dark dark:text-surface-100 transition-colors">
      {/* Placeholder — replace with <Routes> once pages are built */}
      <div className="flex items-center justify-center min-h-screen">
        <h1 className="text-3xl font-bold text-primary-600">
          🌿 MediPlant AI
        </h1>
      </div>

      {/*
        <Routes>
          <Route element={<Layout />}>
            <Route path="/"              element={<Home />} />
            <Route path="/detect"        element={<Detect />} />
            <Route path="/chat"          element={<Chat />} />
            <Route path="/plants"        element={<PlantLibrary />} />
            <Route path="/plants/:id"    element={<PlantDetail />} />
            <Route path="/login"         element={<Login />} />
            <Route path="/register"      element={<Register />} />
            <Route path="*"              element={<NotFound />} />
          </Route>
        </Routes>
      */}
    </div>
  );
}

export default App;
