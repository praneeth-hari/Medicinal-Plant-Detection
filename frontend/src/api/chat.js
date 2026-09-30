/**
 * Chat API Module
 * ================
 *
 * Exposes methods for RAG-powered chat assistant.
 */
import client from './client';
import { API_ROUTES } from '../utils/api';

/**
 * Sends a message to the RAG chat assistant.
 * If sessionId is null, a new session is auto-created.
 * @param {number|null} sessionId
 * @param {string} message
 * @returns {Promise<object>} ChatResponse { session_id, message: ChatMessageResponse }
 */
export async function sendMessage(sessionId, message) {
  // Optional AI preferences saved from the Settings page
  const temperature = parseFloat(localStorage.getItem('mediplant_chat_temp'));
  const maxTokens = parseInt(localStorage.getItem('mediplant_chat_tokens'), 10);
  const response = await client.post(API_ROUTES.CHAT, {
    session_id: sessionId ? parseInt(sessionId, 10) : null,
    message,
    ...(Number.isFinite(temperature) && { temperature }),
    ...(Number.isFinite(maxTokens) && { max_tokens: maxTokens }),
  });
  return response.data;
}

/**
 * Lists the authenticated user's chat sessions.
 * @returns {Promise<Array>} List of ChatSessionResponse
 */
export async function getSessions() {
  const response = await client.get(API_ROUTES.CHAT_SESSIONS);
  return response.data;
}

/**
 * Fetches message history for a specific chat session.
 * @param {number|string} sessionId
 * @returns {Promise<Array>} List of ChatMessageResponse
 */
export async function getSessionMessages(sessionId) {
  const response = await client.get(`${API_ROUTES.CHAT_SESSIONS}/${sessionId}`);
  return response.data;
}
