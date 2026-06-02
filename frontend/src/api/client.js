/**
 * Axios HTTP client instance.
 *
 * Provides a pre-configured Axios instance with:
 * - baseURL sourced from env
 * - Request interceptor that attaches the JWT auth token
 * - Response interceptor for centralised error handling
 */
import axios from 'axios';
import { LOCAL_STORAGE_KEYS } from '../utils/constants';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// ── Request interceptor — attach auth token ──────────────
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response interceptor — centralised error handling ────
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // TODO: implement global error toasts, 401 redirect, etc.
    if (error.response?.status === 401) {
      localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
      // Optionally redirect to /login
    }
    return Promise.reject(error);
  },
);

export default client;
