/**
 * Auth API module.
 *
 * Provides functions for user authentication — login, registration,
 * and profile retrieval.
 */
import client from './client';

/**
 * Log in with email and password.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function login(email, password) {
  // TODO: implement
  return client.post('/auth/login', { email, password });
}

/**
 * Register a new user account.
 * @param {{ name: string, email: string, password: string }} data
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function register(data) {
  // TODO: implement
  return client.post('/auth/register', data);
}

/**
 * Get the profile of the currently authenticated user.
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function getProfile() {
  // TODO: implement
  return client.get('/auth/profile');
}
