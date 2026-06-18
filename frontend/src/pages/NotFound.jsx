/**
 * NotFound Page Scaffold
 * ======================
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sprout, HelpCircle } from 'lucide-react';
import Button from '../components/common/Button';

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] p-6 text-center">
      <div className="flex items-center justify-center w-16 h-16 rounded-full bg-surface-100 dark:bg-surface-800 text-surface-500 mb-6 border border-surface-200 dark:border-surface-700">
        <HelpCircle className="w-8 h-8 animate-pulse" />
      </div>
      
      <h1 className="text-4xl font-extrabold text-surface-900 dark:text-white tracking-tight mb-2">
        404
      </h1>
      <h2 className="text-xl font-bold text-surface-800 dark:text-surface-200 mb-3">
        Page Not Found
      </h2>
      <p className="text-sm text-surface-500 dark:text-surface-400 max-w-sm mb-8 leading-relaxed">
        The page you are looking for does not exist or has been moved to a new section.
      </p>

      <Button onClick={() => navigate('/')} variant="primary">
        Go Back Home
      </Button>
    </div>
  );
}

export default NotFound;
