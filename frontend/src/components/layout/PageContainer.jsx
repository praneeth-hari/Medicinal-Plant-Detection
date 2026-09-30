/**
 * PageContainer Component
 * =======================
 *
 * Provides a responsive layout wrapper with standard padding around main contents.
 */

export function PageContainer({ children, className = '' }) {
  return (
    <main className={`flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto ${className}`}>
      {children}
    </main>
  );
}

export default PageContainer;
