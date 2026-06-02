/**
 * Form / input validation utilities.
 *
 * Pure functions that return `true` when the value is valid
 * or an error message string when invalid.
 */

/**
 * Validate an email address.
 * @param {string} email
 * @returns {true|string} `true` if valid, otherwise an error message
 */
export function validateEmail(email) {
  // TODO: refine regex as needed
  if (!email) return 'Email is required';
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email) ? true : 'Please enter a valid email address';
}

/**
 * Validate a password against strength rules.
 * @param {string} password
 * @returns {true|string} `true` if valid, otherwise an error message
 */
export function validatePassword(password) {
  // TODO: refine rules
  if (!password) return 'Password is required';
  if (password.length < 8) return 'Password must be at least 8 characters';
  return true;
}
