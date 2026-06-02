/**
 * Detection API module.
 *
 * Provides functions for uploading plant images for AI detection
 * and retrieving past detection history.
 */
import client from './client';

/**
 * Upload an image for medicinal plant detection.
 * @param {File} imageFile - The image file to analyse
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function detectPlant(imageFile) {
  // TODO: implement
  const formData = new FormData();
  formData.append('image', imageFile);

  return client.post('/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

/**
 * Retrieve the authenticated user's detection history.
 * @param {object} [params] - Pagination / filter params
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function getDetectionHistory(params = {}) {
  // TODO: implement
  return client.get('/detect/history', { params });
}
