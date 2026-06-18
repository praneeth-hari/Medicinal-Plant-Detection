/**
 * Reusable SearchBar Component
 * ============================
 */
import React from 'react';
import { Search, X } from 'lucide-react';

export function SearchBar({
  value,
  onChange,
  onClear,
  placeholder = 'Search...',
  className = '',
}) {
  return (
    <div className={`relative flex items-center w-full max-w-md ${className}`}>
      <Search className="absolute left-3 w-4 h-4 text-surface-400 pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full pl-9 pr-8 py-2 text-sm rounded-lg border border-surface-300 dark:border-surface-750 bg-white dark:bg-surface-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-surface-900 dark:text-white"
      />
      {value && onClear && (
        <button
          onClick={onClear}
          className="absolute right-3 p-0.5 rounded-md hover:bg-surface-100 dark:hover:bg-surface-700 text-surface-400 hover:text-surface-600 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}

export default SearchBar;
