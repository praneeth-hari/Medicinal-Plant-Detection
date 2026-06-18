/**
 * RoleRoute — Role-based route guard.
 *
 * Renders child routes only when the authenticated user has the
 * required role.  Redirects to the dashboard with an informational
 * message if the role check fails.
 *
 * Usage:
 *   <Route element={<RoleRoute requiredRole="developer" />}>
 *     <Route path="/control-tower" element={<ControlTower />} />
 *   </Route>
 */
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { ROUTES } from '../../utils/routes';

export function RoleRoute({ requiredRole = 'developer' }) {
  const { role, isAuthenticated, loading } = useAuth();

  if (loading) return null;

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  if (role !== requiredRole) {
    return <Navigate to={ROUTES.DASHBOARD} replace />;
  }

  return <Outlet />;
}

export default RoleRoute;
