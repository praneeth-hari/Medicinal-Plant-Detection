/**
 * Reusable Button Component
 * =========================
 */
import React from 'react';
import Loader from './Loader';

export function Button({
  children,
  type = 'button',
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  onClick,
  ...props
}) {
  const baseStyle = 'inline-flex items-center justify-center font-medium rounded-lg transition-all focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variants = {
    primary: 'bg-primary-500 hover:bg-primary-600 text-white focus-visible:ring-primary-500 shadow-glow-sm hover:shadow-glow',
    secondary: 'bg-surface-100 border border-surface-200 hover:bg-surface-200 text-surface-800 dark:bg-white/5 dark:border-white/10 dark:text-white dark:hover:bg-white/10 focus-visible:ring-primary-500',
    danger: 'bg-red-650 hover:bg-red-750 text-white focus-visible:ring-red-500',
    ghost: 'hover:bg-surface-100 text-surface-700 dark:hover:bg-white/5 dark:text-surface-200 focus-visible:ring-primary-500',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {isLoading && <Loader className="w-4 h-4 mr-2 border-current" />}
      {children}
    </button>
  );
}

export default Button;
