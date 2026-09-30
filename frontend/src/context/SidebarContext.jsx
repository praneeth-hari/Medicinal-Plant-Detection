/**
 * SidebarContext — React context to control sidebar open / collapsed state.
 *
 * Manages responsive sidebar toggle states across layouts.
 */
import { createContext, useState, useCallback, useMemo } from 'react';

// eslint-disable-next-line react-refresh/only-export-components
export const SidebarContext = createContext(null);

export function SidebarProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false); // Mobile drawer visibility
  const [isCollapsed, setIsCollapsed] = useState(false); // Desktop collapsed view

  const toggleSidebar = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const openSidebar = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeSidebar = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleCollapse = useCallback(() => {
    setIsCollapsed((prev) => !prev);
  }, []);

  const value = useMemo(
    () => ({
      isOpen,
      isCollapsed,
      toggleSidebar,
      openSidebar,
      closeSidebar,
      toggleCollapse,
    }),
    [isOpen, isCollapsed, toggleSidebar, openSidebar, closeSidebar, toggleCollapse]
  );

  return (
    <SidebarContext.Provider value={value}>
      {children}
    </SidebarContext.Provider>
  );
}

export default SidebarProvider;
