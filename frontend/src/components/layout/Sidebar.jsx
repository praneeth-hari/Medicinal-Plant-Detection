/**
 * Sidebar Component
 * =================
 *
 * Renders the primary navigation menu. Supports collapsing, slide-out drawer on mobile,
 * and active state highlighting using react-router-dom NavLink.
 */
import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Sprout,
  Scan,
  MessageSquare,
  BookOpen,
  ArrowLeftRight,
  History,
  Heart,
  Settings,
  Info,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Shield,
} from 'lucide-react';
import { ROUTES } from '../../utils/routes';
import { useSidebar } from '../../hooks/useSidebar';
import { useAuth } from '../../hooks/useAuth';

export function Sidebar() {
  const { isOpen, isCollapsed, toggleCollapse, closeSidebar } = useSidebar();
  const { logout, user, isDeveloper } = useAuth();

  const allMenuItems = [
    { name: 'Dashboard',        path: ROUTES.DASHBOARD,       icon: LayoutDashboard, devOnly: false },
    { name: 'Plant Catalog',    path: '/plants',               icon: Sprout,          devOnly: false },
    { name: 'Plant Detection',  path: ROUTES.PLANT_DETECTION,  icon: Scan,            devOnly: false },
    { name: 'RAG Assistant',    path: ROUTES.RAG_ASSISTANT,    icon: MessageSquare,   devOnly: false },
    { name: 'Research Papers',  path: ROUTES.RESEARCH_PAPERS,  icon: BookOpen,        devOnly: false },
    { name: 'Plant Comparison', path: ROUTES.COMPARISON,       icon: ArrowLeftRight,  devOnly: false },
    { name: 'History',          path: ROUTES.HISTORY,          icon: History,         devOnly: false },
    { name: 'Favorites',        path: ROUTES.FAVORITES,        icon: Heart,           devOnly: false },
    { name: 'Settings',         path: ROUTES.SETTINGS,         icon: Settings,        devOnly: false },
    { name: 'AI Control Tower', path: ROUTES.CONTROL_TOWER,    icon: Shield,          devOnly: true  },
    { name: 'About',            path: ROUTES.ABOUT,            icon: Info,            devOnly: false },
  ];

  const menuItems = allMenuItems.filter(item => !item.devOnly || isDeveloper);

  return (
    <aside
      className={`fixed top-0 bottom-0 left-0 z-40 flex flex-col glass border-r border-surface-200 dark:border-white/10 transition-all duration-300 ${
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      } ${isCollapsed ? 'w-20' : 'w-64'}`}
    >
      {/* Branding */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-surface-200 dark:border-white/10">
        <div className={`flex items-center gap-2 font-bold text-primary-500 dark:text-primary-400 ${isCollapsed ? 'justify-center w-full' : ''}`}>
          <Sprout className="w-6 h-6 text-primary-600 flex-shrink-0 animate-bounce" />
          {!isCollapsed && <span className="text-lg tracking-tight bg-gradient-to-r from-primary-650 to-accent-500 bg-clip-text text-transparent">MediPlant AI</span>}
        </div>
        {/* Collapse Button - Desktop Only */}
        <button
          onClick={toggleCollapse}
          className="hidden lg:flex p-1.5 rounded-lg hover:bg-primary-500/10 text-surface-400 transition-colors"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1.5">
        {menuItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            onClick={closeSidebar}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 group relative border border-transparent ${
                isActive
                  ? 'bg-primary-500/10 border-primary-500/25 text-primary-700 dark:text-primary-400 shadow-glow-sm'
                  : 'text-surface-600 hover:text-surface-900 hover:bg-primary-500/5 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-primary-400/5'
              }`
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0 transition-colors" />
            {!isCollapsed && <span>{item.name}</span>}
            
            {/* Tooltip for Collapsed Sidebar */}
            {isCollapsed && (
              <span className="absolute left-14 z-55 scale-0 group-hover:scale-100 rounded bg-surface-900 px-2 py-1 text-xs text-white transition-all whitespace-nowrap">
                {item.name}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer / User Profile */}
      <div className="p-4 border-t border-surface-200 dark:border-white/10">
        <button
          onClick={logout}
          className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-semibold text-red-650 hover:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/10 transition-colors group relative`}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!isCollapsed && <span>Sign Out</span>}
          
          {isCollapsed && (
            <span className="absolute left-14 scale-0 group-hover:scale-100 rounded bg-red-900 px-2 py-1 text-xs text-white transition-all whitespace-nowrap">
              Sign Out
            </span>
          )}
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
