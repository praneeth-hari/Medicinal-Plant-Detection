/**
 * Axios HTTP client instance.
 *
 * Provides a pre-configured Axios instance with:
 * - baseURL sourced from env config
 * - Request interceptor that attaches the JWT auth token
 * - Response interceptor for centralised error handling (401, 500)
 */
import axios from 'axios';
import config from '../config/config';
import { LOCAL_STORAGE_KEYS } from '../utils/constants';

const client = axios.create({
  baseURL: config.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 180000,
});

// Request Interceptor: Attach token if it exists
client.interceptors.request.use(
  (reqConfig) => {
    const token = localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      reqConfig.headers.Authorization = `Bearer ${token}`;
    }
    return reqConfig;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Centralised error handling
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    
    if (status === 401) {
      // Clear token and user on unauthorized response
      localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
      
      // Optionally reload the page to trigger app-level redirect to login
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    } else if (status >= 500) {
      console.error('Server error occurred:', error.response?.data || error.message);
    }
    
    return Promise.reject(error);
  }
);

export default client;
