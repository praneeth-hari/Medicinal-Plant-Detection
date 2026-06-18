/**
 * PrivateRoute Guard
 * ==================
 *
 * Redirects unauthorized users to `/login` while showing a loading spinner during boot session restoration.
 */
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import Loader from '../common/Loader';

export function PrivateRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-background-light dark:bg-background-dark">
        <Loader className="w-10 h-10 text-primary-650" />
        <p className="mt-4 text-sm text-surface-500 font-medium">Verifying credentials...</p>
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

export default PrivateRoute;
