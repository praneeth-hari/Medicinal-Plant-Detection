/**
 * Reusable Input Component
 * ========================
 */
import React from 'react';

export const Input = React.forwardRef(({
  label,
  type = 'text',
  name,
  value,
  onChange,
  error,
  placeholder,
  className = '',
  disabled = false,
  required = false,
  ...props
}, ref) => {
  return (
    <div className={`flex flex-col gap-1.5 w-full ${className}`}>
      {label && (
        <label className="text-sm font-medium text-surface-700 dark:text-surface-300">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={`w-full px-4 py-2.5 text-xs rounded-xl border bg-white border-surface-200 dark:bg-black/40 dark:border-white/10 text-surface-900 dark:text-white placeholder-surface-400 dark:placeholder-surface-450 transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 disabled:opacity-40 disabled:bg-transparent ${
          error
            ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500'
            : 'border-surface-200 dark:border-white/10 focus:ring-primary-500/20 focus:border-primary-500'
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

Input.displayName = 'Input';

export default Input;
