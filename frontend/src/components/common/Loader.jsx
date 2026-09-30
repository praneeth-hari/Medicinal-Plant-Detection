/**
 * Reusable Loader (Spinner) Component
 * ===================================
 */

export function Loader({ className = 'w-6 h-6 text-primary-600', ...props }) {
  return (
    <div
      className={`animate-spin rounded-full border-2 border-t-transparent ${className}`}
      role="status"
      {...props}
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}

export default Loader;
