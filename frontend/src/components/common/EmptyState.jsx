/**
 * Reusable EmptyState Component
 * =============================
 */
import Button from './Button';

export function EmptyState({
  title = 'No records found',
  description = 'There is nothing to display here yet.',
  icon: Icon,
  actionText,
  onAction,
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 border border-dashed border-surface-200 rounded-xl dark:border-surface-800 bg-surface-50/50 dark:bg-surface-900/10">
      {Icon && <Icon className="w-12 h-12 text-surface-400 mb-4" />}
      <h3 className="text-lg font-semibold text-surface-900 dark:text-white mb-1">
        {title}
      </h3>
      <p className="text-sm text-surface-500 dark:text-surface-400 max-w-sm mb-6">
        {description}
      </p>
      {actionText && onAction && (
        <Button onClick={onAction} variant="primary">
          {actionText}
        </Button>
      )}
    </div>
  );
}

export default EmptyState;
