/**
 * ThemeContext — Application Theme Provider (Light Mode).
 */
import { createContext, useMemo, useEffect } from 'react';
import { LOCAL_STORAGE_KEYS } from '../utils/constants';

// eslint-disable-next-line react-refresh/only-export-components
export const ThemeContext = createContext(null);

/**
 * ThemeProvider — wraps children with light theme state.
 * @param {{ children: React.ReactNode }} props
 * @returns {JSX.Element}
 */
export function ThemeProvider({ children }) {
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('dark');
    localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, 'light');
  }, []);

  const value = useMemo(
    () => ({
      theme: 'light',
      isDark: false,
      toggleTheme: () => {},
      setTheme: () => {},
    }),
    [],
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export default ThemeProvider;
