/**
 * Auth API Module
 * ================
 *
 * Exposes methods for logging in, registering, and retrieving the current user's profile.
 */
import client from './client';
import { API_ROUTES } from '../utils/api';

/**
 * Logs in a user using email and password.
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise<object>} Token payload
 */
export async function login(email, password) {
  const response = await client.post(API_ROUTES.AUTH_LOGIN, { email, password });
  return response.data;
}

/**
 * Registers a new user.
 * @param {object} userData { username, email, password }
 * @returns {Promise<object>} User detail response
 */
export async function register(userData) {
  const response = await client.post(API_ROUTES.AUTH_REGISTER, userData);
  return response.data;
}

/**
 * Retrieves the current authenticated user's profile.
 * @returns {Promise<object>} User profile details
 */
export async function getProfile() {
  const response = await client.get(API_ROUTES.AUTH_ME);
  return response.data;
}

export async function changePassword(currentPassword, newPassword) {
  await client.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
}
