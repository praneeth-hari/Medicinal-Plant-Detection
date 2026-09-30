/**
 * Application-wide constants.
 *
 * Centralises API route paths, localStorage key names,
 * and other default configuration values.
 */

// NOTE: API route constants are defined in utils/api.js.
// Do NOT define API_ROUTES here to avoid path inconsistencies.

/** Keys used to persist data in localStorage */
export const LOCAL_STORAGE_KEYS = {
  THEME:       'mediplant_theme',
};

/** Default / fallback values */
export const DEFAULTS = {
  PAGE_SIZE:       12,
  MAX_FILE_SIZE:   5 * 1024 * 1024, // 5 MB
  ACCEPTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  APP_NAME:        import.meta.env.VITE_APP_NAME || 'MediPlant AI',
};
