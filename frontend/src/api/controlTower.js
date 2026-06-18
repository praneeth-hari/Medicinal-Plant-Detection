/**
 * Control Tower API Module
 * ========================
 *
 * Exposes methods for managing governance settings, retrieving telemetry
 * statistics, and viewing compliance audit logs.
 */
import client from './client';
import { API_ROUTES } from '../utils/api';

/**
 * Fetches the active control tower settings.
 * @returns {Promise<object>} ControlTowerSettings
 */
export async function getSettings() {
  const response = await client.get(API_ROUTES.CONTROL_TOWER_SETTINGS);
  return response.data;
}

/**
 * Updates the active control tower settings.
 * @param {object} settings
 * @returns {Promise<object>} Updated ControlTowerSettings
 */
export async function updateSettings(settings) {
  const response = await client.post(API_ROUTES.CONTROL_TOWER_SETTINGS, settings);
  return response.data;
}

/**
 * Fetches the live control tower system telemetry statistics.
 * @returns {Promise<object>} ControlTowerStats
 */
export async function getStats() {
  const response = await client.get(API_ROUTES.CONTROL_TOWER_STATS);
  return response.data;
}

/**
 * Fetches the compliance query audit logs.
 * @returns {Promise<Array>} List of AuditLogEntry
 */
export async function getAuditLogs() {
  const response = await client.get(API_ROUTES.CONTROL_TOWER_AUDIT);
  return response.data;
}
