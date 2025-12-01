/**
 * Magic Link API - Passwordless authentication
 */
import apiClient from './client'

const magicLinkAPI = {
  /**
   * Request a magic link for passwordless login
   * @param {string} email - User email address
   */
  requestMagicLink(email) {
    return apiClient.post('/api/v1/auth/magic-links/', { email })
  },

  /**
   * Verify magic link token and authenticate
   * @param {string} token - Magic link token
   */
  verifyMagicLink(token) {
    return apiClient.post('/api/v1/auth/magic-link-verification/', { token })
  }
}

export default magicLinkAPI

