/**
 * React Error Boundary
 * ====================
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 */
import React from 'react';
import ErrorState from './ErrorState';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to console or monitoring service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="flex items-center justify-center min-h-[400px] p-6">
          <ErrorState
            title="Application Error"
            message={this.state.error?.message || 'An unexpected rendering error occurred.'}
            onRetry={this.handleReset}
            retryText="Reload View"
          />
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
