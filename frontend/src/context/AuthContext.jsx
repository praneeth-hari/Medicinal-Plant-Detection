/**
 * AuthContext — React context for authentication state.
 *
 * Provides user data, auth status, and login/logout/register
 * actions to the entire component tree.
 */
import { createContext, useState, useEffect, useMemo } from 'react';
import { LOCAL_STORAGE_KEYS } from '../utils/constants';

export const AuthContext = createContext(null);

/**
 * AuthProvider — wraps children with auth state.
 * @param {{ children: React.ReactNode }} props
 * @returns {JSX.Element}
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: check for existing token and fetch user profile
    const token = localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      // fetchProfile and setUser
    }
    setLoading(false);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: !!user,
      login: async () => { /* TODO */ },
      logout: () => {
        localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
        setUser(null);
      },
      register: async () => { /* TODO */ },
    }),
    [user, loading],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
