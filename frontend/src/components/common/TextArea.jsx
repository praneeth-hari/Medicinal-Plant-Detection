/**
 * Reusable TextArea Component
 * ===========================
 */
import React from 'react';

export const TextArea = React.forwardRef(({
  label,
  name,
  value,
  onChange,
  error,
  placeholder,
  className = '',
  disabled = false,
  required = false,
  rows = 4,
  ...props
}, ref) => {
  return (
    <div className={`flex flex-col gap-1.5 w-full ${className}`}>
      {label && (
        <label className="text-sm font-medium text-surface-700 dark:text-surface-300">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <textarea
        ref={ref}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        rows={rows}
        className={`w-full px-3 py-2 text-sm rounded-lg border bg-white dark:bg-surface-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 disabled:opacity-50 disabled:bg-surface-50 dark:disabled:bg-surface-900 ${
          error
            ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500'
            : 'border-surface-300 dark:border-surface-700 focus:ring-primary-500/20 focus:border-primary-500'
        }`}
        {...props}
      />
      {error && (
        <span className="text-xs text-red-600 dark:text-red-400 font-medium">
          {error}
        </span>
      )}
    </div>
  );
});

TextArea.displayName = 'TextArea';

export default TextArea;
