/**
 * Axios HTTP client instance.
 *
 * Provides a pre-configured Axios instance with:
 * - baseURL sourced from env config
 * - Response interceptor for centralised error handling (500)
 */
import axios from 'axios';
import config from '../config/config';

const client = axios.create({
  baseURL: config.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 180000,
});

// Response Interceptor: Centralised error handling
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    
    if (status >= 500) {
      console.error('Server error occurred:', error.response?.data || error.message);
    }
    
    return Promise.reject(error);
  }
);

export default client;
