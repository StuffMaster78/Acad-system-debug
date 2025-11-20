/**
 * Authentication API Service
 * 
 * Complete authentication API service for frontend integration.
 * Copy this file to your frontend project: src/api/auth.js
 * 
 * Usage:
 * import { authApi } from '@/api/auth'
 * await authApi.login(email, password)
 */

import apiClient from './client' // Adjust import path as needed

export const authApi = {
  /**
   * Login with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @param {boolean} rememberMe - Remember user session
   * @returns {Promise} Response with access_token, refresh_token, and user data
   */
  login: (email, password, rememberMe = false) => {
    return apiClient.post('/auth/auth/login/', {
      email,
      password,
      remember_me: rememberMe
    })
  },

  /**
   * Logout current user
   * @param {boolean} logoutAll - Logout from all devices
   * @returns {Promise} Success message
   */
  logout: (logoutAll = false) => {
    return apiClient.post('/auth/auth/logout/', {
      logout_all: logoutAll
    })
  },

  /**
   * Refresh access token using refresh token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise} New access_token and refresh_token
   */
  refreshToken: (refreshToken) => {
    return apiClient.post('/auth/auth/refresh-token/', {
      refresh_token: refreshToken
    })
  },

  /**
   * Change password for authenticated user
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @param {string} confirmPassword - Password confirmation
   * @returns {Promise} Success message
   */
  changePassword: (currentPassword, newPassword, confirmPassword) => {
    return apiClient.post('/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  },

  /**
   * Request password reset link
   * @param {string} email - User email
   * @returns {Promise} Success message (always returns success for security)
   */
  requestPasswordReset: (email) => {
    return apiClient.post('/auth/password-reset/', {
      email
    })
  },

  /**
   * Confirm password reset with token
   * @param {string} token - Reset token from email
   * @param {string} password - New password
   * @returns {Promise} Success message
   */
  confirmPasswordReset: (token, password) => {
    return apiClient.post('/auth/password-reset/confirm/', {
      token,
      password
    })
  },

  /**
   * Request magic link for passwordless login
   * @param {string} email - User email
   * @returns {Promise} Success message
   */
  requestMagicLink: (email) => {
    return apiClient.post('/auth/magic-link/request/', {
      email
    })
  },

  /**
   * Verify magic link token and get JWT tokens
   * @param {string} token - Magic link token from email
   * @returns {Promise} Response with access_token, refresh_token, and user data
   */
  verifyMagicLink: (token) => {
    return apiClient.post('/auth/magic-link/verify/', {
      token
    })
  },

  /**
   * Setup 2FA (TOTP)
   * @returns {Promise} Response with secret, QR code, and backup codes
   */
  setup2FA: () => {
    return apiClient.post('/auth/2fa/totp/setup/')
  },

  /**
   * Verify 2FA code
   * @param {string} code - TOTP code
   * @returns {Promise} Success message
   */
  verify2FA: (code) => {
    return apiClient.post('/auth/2fa/totp/verify/', {
      code
    })
  },

  /**
   * Get active user sessions
   * @returns {Promise} List of active sessions
   */
  getActiveSessions: () => {
    return apiClient.get('/auth/user-sessions/')
  },

  /**
   * Request account unlock
   * @param {string} email - User email
   * @returns {Promise} Success message
   */
  requestAccountUnlock: (email) => {
    return apiClient.post('/auth/account-unlock/', {
      email
    })
  },

  /**
   * Confirm account unlock with token
   * @param {string} token - Unlock token from email
   * @returns {Promise} Success message
   */
  confirmAccountUnlock: (token) => {
    return apiClient.post('/auth/account-unlock/confirm/', {
      token
    })
  },

  /**
   * Get current user profile
   * @returns {Promise} User profile data
   */
  getCurrentUser: () => {
    return apiClient.get('/auth/user/')
  },

  /**
   * Update user profile
   * @param {Object} data - User data to update
   * @returns {Promise} Updated user data
   */
  updateProfile: (data) => {
    return apiClient.patch('/auth/user/', data)
  }
}

export default authApi

