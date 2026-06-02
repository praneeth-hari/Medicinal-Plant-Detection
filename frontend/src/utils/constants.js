/**
 * Application-wide constants.
 *
 * Centralises API route paths, localStorage key names,
 * and other default configuration values.
 */

/** API route segments (appended to the base URL) */
export const API_ROUTES = {
  AUTH_LOGIN:      '/auth/login',
  AUTH_REGISTER:   '/auth/register',
  AUTH_PROFILE:    '/auth/profile',
  PLANTS:          '/plants',
  PLANTS_SEARCH:   '/plants/search',
  DETECT:          '/detect',
  DETECT_HISTORY:  '/detect/history',
  CHAT_MESSAGE:    '/chat/message',
  CHAT_SESSIONS:   '/chat/sessions',
};

/** Keys used to persist data in localStorage */
export const LOCAL_STORAGE_KEYS = {
  AUTH_TOKEN:  'mediplant_auth_token',
  THEME:       'mediplant_theme',
  USER:        'mediplant_user',
};

/** Default / fallback values */
export const DEFAULTS = {
  PAGE_SIZE:       12,
  MAX_FILE_SIZE:   5 * 1024 * 1024, // 5 MB
  ACCEPTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  APP_NAME:        import.meta.env.VITE_APP_NAME || 'MediPlant AI',
};
