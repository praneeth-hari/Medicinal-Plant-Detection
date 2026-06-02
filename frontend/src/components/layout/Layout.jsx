/**
 * Layout — page-level layout wrapper.
 *
 * Renders Header, an <Outlet /> for routed page content, and Footer.
 * Provides consistent page chrome across all routes.
 */
import { Outlet } from 'react-router-dom';

/**
 * @returns {JSX.Element}
 */
export function Layout() {
  return (
    <div className="layout flex min-h-screen flex-col">
      {/* TODO: <Header /> */}
      <main className="flex-1">
        <Outlet />
      </main>
      {/* TODO: <Footer /> */}
    </div>
  );
}

export default Layout;
