/**
 * AuthContext — React context for authentication state.
 *
 * Provides user data, auth status, loading state, and auth actions.
 */
import { createContext, useState, useEffect, useMemo, useCallback } from 'react';
import { LOCAL_STORAGE_KEYS } from '../utils/constants';
import * as authApi from '../api/auth';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore session on boot
  const restoreSession = useCallback(async () => {
    const token = localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
    if (!token) {
      setLoading(false);
      return;
    }
    
    try {
      const profile = await authApi.getProfile();
      setUser(profile);
    } catch (err) {
      console.error('Session restoration failed:', err);
      localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    try {
      const tokenData = await authApi.login(email, password);
      localStorage.setItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN, tokenData.access_token);
      const profile = await authApi.getProfile();
      setUser(profile);
      localStorage.setItem(LOCAL_STORAGE_KEYS.USER, JSON.stringify(profile));
      return profile;
    } catch (err) {
      localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
      setUser(null);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (username, email, password) => {
    setLoading(true);
    try {
      const newUser = await authApi.register({ username, email, password, role: 'customer' });
      // Authenticate immediately after registering
      const tokenData = await authApi.login(email, password);
      localStorage.setItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN, tokenData.access_token);
      const profile = await authApi.getProfile();
      setUser(profile);
      localStorage.setItem(LOCAL_STORAGE_KEYS.USER, JSON.stringify(profile));
      return profile;
    } catch (err) {
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: !!user,
      role: user?.role ?? 'customer',
      isDeveloper: user?.role === 'developer',
      login,
      logout,
      register,
    }),
    [user, loading, login, logout, register]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
