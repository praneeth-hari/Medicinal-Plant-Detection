/**
 * TopNav Component
 * ================
 *
 * Renders the top bar. Includes dark / light theme toggling, hamburger menu trigger
 * for mobile viewports.
 */
import { Menu } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';
import { useTheme } from '../../hooks/useTheme';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

export function TopNav() {
  const { openSidebar } = useSidebar();
  const { isDark, toggleTheme } = useTheme();
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

      <div className="flex items-center gap-2">
        {/* Animated Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="relative flex items-center p-1 rounded-full bg-black/5 dark:bg-black/40 border border-surface-200 dark:border-white/10 select-none cursor-pointer w-28 h-9"
          aria-label="Toggle theme"
        >
          <div className={`flex items-center justify-center gap-1 w-1/2 text-[10px] font-bold z-10 transition-colors duration-300 ${isDark ? 'text-surface-400' : 'text-primary-650'}`}>
            ☀️ Light
          </div>
          <div className={`flex items-center justify-center gap-1 w-1/2 text-[10px] font-bold z-10 transition-colors duration-300 ${isDark ? 'text-primary-450' : 'text-surface-500 dark:text-surface-400'}`}>
            🌙 Dark
          </div>
          <motion.div
            layout
            transition={{ type: 'spring', stiffness: 350, damping: 25 }}
            className="absolute top-1 bottom-1 w-[calc(50%-4px)] rounded-full bg-white dark:bg-primary-500/20 border border-surface-200 dark:border-primary-500/35 shadow-sm"
            style={{
              left: isDark ? '50%' : '4px'
            }}
          />
        </button>

      </div>
    </header>
  );
}

export default TopNav;
