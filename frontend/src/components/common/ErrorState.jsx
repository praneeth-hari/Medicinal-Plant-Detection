/**
 * Reusable ErrorState Component
 * ============================
 */
import { AlertCircle } from 'lucide-react';
import Button from './Button';

export function ErrorState({
  title = 'Something went wrong',
  message = 'An error occurred while loading this section. Please try again.',
  onRetry,
  retryText = 'Retry',
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 border border-red-100 rounded-xl dark:border-red-950/20 bg-red-50/50 dark:bg-red-950/5">
      <AlertCircle className="w-12 h-12 text-red-500 mb-4 animate-pulse" />
      <h3 className="text-lg font-semibold text-red-800 dark:text-red-400 mb-1">
        {title}
      </h3>
      <p className="text-sm text-red-650 dark:text-red-300 max-w-sm mb-6 font-medium">
        {message}
      </p>
      {onRetry && (
        <Button onClick={onRetry} variant="secondary" className="border-red-200 dark:border-red-900/50 hover:bg-red-100/10">
          {retryText}
        </Button>
      )}
    </div>
  );
}

export default ErrorState;
