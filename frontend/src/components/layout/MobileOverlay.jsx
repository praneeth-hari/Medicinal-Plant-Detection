/**
 * MobileOverlay Component
 * =======================
 *
 * Dark translucent overlay that covers page content behind the mobile sidebar menu drawer.
 * Clicking the overlay triggers the menu to close.
 */
import { useSidebar } from '../../hooks/useSidebar';

export function MobileOverlay() {
  const { isOpen, closeSidebar } = useSidebar();

  if (!isOpen) return null;

  return (
    <div
      onClick={closeSidebar}
      className="fixed inset-0 z-40 bg-surface-950/40 backdrop-blur-sm lg:hidden transition-opacity duration-300"
      aria-hidden="true"
    />
  );
}

export default MobileOverlay;
