/**
 * Config Module
 * =============
 *
 * Validates and exposes environment variables.
 */

const getEnv = (key, defaultValue = undefined) => {
  const val = import.meta.env[key];
  if (val === undefined && defaultValue === undefined) {
    console.warn(`Environment variable ${key} is not defined!`);
  }
  return val !== undefined ? val : defaultValue;
};

const resolveDemoMode = (apiUrl) => {
  const override = import.meta.env.VITE_DEMO_MODE;
  if (override === 'true') return true;
  if (override === 'false') return false;

  // When absent: default to static showcase mode only for a production build whose resolved API URL still points to localhost
  const isProd = Boolean(import.meta.env.PROD);
  const isLocalApi = typeof apiUrl === 'string' && (apiUrl.includes('localhost') || apiUrl.includes('127.0.0.1'));
  return isProd && isLocalApi;
};

const apiUrl = getEnv('VITE_API_URL', 'http://localhost:8000/api/v1');

export const config = {
  API_URL: apiUrl,
  APP_NAME: getEnv('VITE_APP_NAME', 'MediPlant AI'),
  NODE_ENV: import.meta.env.MODE || 'development',
  DEMO_MODE: resolveDemoMode(apiUrl),
};

export default config;
