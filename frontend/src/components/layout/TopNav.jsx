/**
 * TopNav Component
 * ================
 *
 * Renders the top bar. Includes dark / light theme toggling, hamburger menu trigger
 * for mobile viewports.
 */
import { Menu } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';
import { useLocation } from 'react-router-dom';

export function TopNav() {
  const { openSidebar } = useSidebar();
  const location = useLocation();

  // Helper to construct a breadcrumb title from the path
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/plants')) return 'Plant Catalog';
    if (path === '/detect') return 'Plant Detection';
    if (path === '/chat') return 'RAG Chat Assistant';
    if (path === '/papers') return 'Research Papers';
    if (path === '/comparison') return 'Plant Comparison';
    if (path === '/history') return 'Inference & Chat History';
    if (path === '/favorites') return 'Favorites';
    if (path === '/settings') return 'Settings';
    if (path === '/about') return 'About MediPlant';
    return 'MediPlant AI';
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 glass border-b border-surface-200 dark:border-white/10 dark:bg-black/25 backdrop-blur-md transition-all duration-300">
      <div className="flex items-center gap-4">
        {/* Mobile Hamburger menu */}
        <button
          onClick={openSidebar}
          className="p-2 rounded-lg lg:hidden hover:bg-surface-100 dark:hover:bg-surface-800 text-surface-500"
          aria-label="Open sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Breadcrumb Title */}
        <h2 className="text-sm font-semibold tracking-tight text-surface-850 dark:text-surface-200 hidden sm:block">
          {getPageTitle()}
        </h2>
      </div>
    </header>
  );
}

export default TopNav;
