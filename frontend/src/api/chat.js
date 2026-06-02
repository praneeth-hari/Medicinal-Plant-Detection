/**
 * Chat API module.
 *
 * Provides functions for the RAG-powered chat assistant —
 * sending messages, listing sessions, and fetching session history.
 */
import client from './client';

/**
 * Send a message to the RAG assistant.
 * @param {string} sessionId - Chat session ID
 * @param {string} message   - User message text
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function sendMessage(sessionId, message) {
  // TODO: implement
  return client.post('/chat/message', { session_id: sessionId, message });
}

/**
 * Get all chat sessions for the current user.
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function getSessions() {
  // TODO: implement
  return client.get('/chat/sessions');
}

/**
 * Get all messages in a specific chat session.
 * @param {string} sessionId
 * @returns {Promise<import('axios').AxiosResponse>}
 */
export async function getSessionMessages(sessionId) {
  // TODO: implement
  return client.get(`/chat/sessions/${sessionId}/messages`);
}
