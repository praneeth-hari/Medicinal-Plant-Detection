/**
 * Reusable PageHeader Component
 * =============================
 */

export function PageHeader({
  title,
  description,
  actions,
  className = '',
}) {
  return (
    <div className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-surface-150 dark:border-surface-850 mb-6 ${className}`}>
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-surface-900 dark:text-white">
          {title}
        </h1>
        {description && (
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
            {description}
          </p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  );
}

export default PageHeader;
