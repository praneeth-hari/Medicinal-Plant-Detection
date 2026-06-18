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

export const config = {
  API_URL: getEnv('VITE_API_URL', 'http://localhost:8000/api/v1'),
  APP_NAME: getEnv('VITE_APP_NAME', 'MediPlant AI'),
  NODE_ENV: import.meta.env.MODE || 'development',
};

export default config;
