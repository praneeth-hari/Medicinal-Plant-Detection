/**
 * AppLayout Component
 * ===================
 *
 * Controls layout scaffolding including desktop sidebar, mobile drawer,
 * topnav bar, and content container.
 */
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './Sidebar';
import TopNav from './TopNav';
import PageContainer from './PageContainer';
import MobileOverlay from './MobileOverlay';
import { useSidebar } from '../../hooks/useSidebar';
import AuroraBackground from '../common/AuroraBackground';

export function AppLayout() {
  const { isCollapsed } = useSidebar();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background-light dark:bg-[#04130a] transition-colors duration-500 relative overflow-hidden">
      {/* Global Aurora Background */}
      <AuroraBackground />

      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Mobile drawer backdrop */}
        <MobileOverlay />

        {/* Navigation sidebar */}
        <Sidebar />

        {/* Main content column */}
        <div
          className={`flex flex-col min-h-screen transition-all duration-300 ${
            isCollapsed ? 'lg:pl-20' : 'lg:pl-64'
          }`}
        >
          <TopNav />
          <PageContainer>
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25, ease: 'easeInOut' }}
                className="w-full flex-1 flex flex-col"
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </PageContainer>
        </div>
      </div>
    </div>
  );
}

export default AppLayout;
