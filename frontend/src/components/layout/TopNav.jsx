/**
 * TopNav Component
 * ================
 *
 * Renders the top bar. Includes dark / light theme toggling, hamburger menu trigger
 * for mobile viewports, and user profile displays.
 */
import React from 'react';
import { Menu, Sun, Moon, User } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';
import { useTheme } from '../../hooks/useTheme';
import { useAuth } from '../../hooks/useAuth';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

export function TopNav() {
  const { openSidebar } = useSidebar();
  const { isDark, toggleTheme } = useTheme();
  const { user, isDeveloper } = useAuth();
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

        {/* User Badge */}
        {user && (
          <div className="flex items-center gap-2 pl-2 border-l border-surface-200 dark:border-white/10">
            <div className="flex flex-col text-right hidden md:flex">
              <span className="text-xs font-semibold text-surface-900 dark:text-white leading-none">
                {user.username}
              </span>
              {/* Role badge */}
              <span className={`text-[10px] font-bold mt-0.5 leading-none px-1.5 py-0.5 rounded-full self-end ${
                isDeveloper
                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400 border border-amber-200 dark:border-amber-700/40'
                  : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-700/40'
              }`}>
                {isDeveloper ? 'Developer' : 'Customer'}
              </span>
            </div>
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-950/40 text-primary-700 dark:text-primary-400 font-bold text-xs uppercase border border-primary-200 dark:border-primary-900/50">
              {user.username?.substring(0, 2) || <User className="w-4 h-4" />}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default TopNav;
