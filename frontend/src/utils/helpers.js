/**
 * General-purpose utility / helper functions.
 *
 * Small, pure functions used across the application for
 * formatting, string manipulation, and className merging.
 */

/**
 * Format an ISO date string into a human-readable format.
 * @param {string} isoString - ISO 8601 date string
 * @param {Intl.DateTimeFormatOptions} [options] - Intl format options
 * @returns {string} Formatted date string
 */
export function formatDate(isoString, options = {}) {
  // TODO: implement full formatting logic
  const defaults = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(isoString).toLocaleDateString(undefined, { ...defaults, ...options });
}

/**
 * Truncate text to a given max length, appending an ellipsis.
 * @param {string} text
 * @param {number} [maxLength=100]
 * @returns {string}
 */
export function truncateText(text, maxLength = 100) {
  // TODO: implement
  if (!text) return '';
  return text.length <= maxLength ? text : `${text.slice(0, maxLength)}…`;
}

/**
 * Conditionally join CSS class names (falsy values are ignored).
 * @param  {...(string|false|null|undefined)} classes
 * @returns {string}
 */
export function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}
