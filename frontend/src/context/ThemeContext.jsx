/**
 * ThemeContext — React context for dark / light mode toggle.
 *
 * Persists the user's preference to localStorage and applies
 * the `dark` class to the document element for Tailwind dark mode.
 */
import { createContext, useState, useEffect, useMemo } from 'react';
import { LOCAL_STORAGE_KEYS } from '../utils/constants';

export const ThemeContext = createContext(null);

/**
 * ThemeProvider — wraps children with theme state.
 * @param {{ children: React.ReactNode }} props
 * @returns {JSX.Element}
 */
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEYS.THEME);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, theme);
  }, [theme]);

  const value = useMemo(
    () => ({
      theme,
      isDark: theme === 'dark',
      toggleTheme: () => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark')),
      setTheme,
    }),
    [theme],
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export default ThemeProvider;
