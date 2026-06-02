/**
 * useAuth — custom hook for authentication state.
 *
 * Will provide the current user, login/logout/register actions,
 * loading state, and token management via AuthContext.
 */
import { useContext } from 'react';
// import { AuthContext } from '../context/AuthContext';

/**
 * Access auth state and actions.
 * @returns {{ user: object|null, isAuthenticated: boolean, loading: boolean, login: Function, logout: Function, register: Function }}
 */
export function useAuth() {
  // TODO: implement — consume AuthContext
  // return useContext(AuthContext);
  return {
    user: null,
    isAuthenticated: false,
    loading: false,
    login: async () => {},
    logout: () => {},
    register: async () => {},
  };
}

export default useAuth;
