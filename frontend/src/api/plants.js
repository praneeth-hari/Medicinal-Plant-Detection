/**
 * Plants API module.
 *
 * Provides functions for fetching plant data from the backend,
 * including listing, detail retrieval, and search.
 */
import client from './client';

/**
 * Fetch a paginated list of plants.
 * @param {object} [params] - Query parameters (page, limit, etc.)
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function getPlants(params = {}) {
  // TODO: implement
  return client.get('/plants', { params });
}

/**
 * Fetch a single plant by ID.
 * @param {string} plantId
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function getPlant(plantId) {
  // TODO: implement
  return client.get(`/plants/${plantId}`);
}

/**
 * Search plants by query string.
 * @param {string} query
 * @param {object} [params] - Additional filters
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function searchPlants(query, params = {}) {
  // TODO: implement
  return client.get('/plants/search', { params: { q: query, ...params } });
}
