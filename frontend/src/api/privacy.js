/**
 * Privacy API - User privacy controls and data access management
 */
import apiClient from './client'

const privacyAPI = {
  /**
   * Get privacy settings
   */
  getSettings() {
    return apiClient.get('/users/privacy/settings/')
  },

  /**
   * Update profile visibility settings
   * @param {Object} visibility - { to_writers, to_admins, to_support }
   */
  updateVisibility(visibility) {
    return apiClient.post('/users/privacy/update-visibility/', visibility)
  },

  /**
   * Update data sharing preferences
   * @param {Object} preferences - { analytics, marketing, third_party }
   */
  updateDataSharing(preferences) {
    return apiClient.post('/users/privacy/update-data-sharing/', preferences)
  },

  /**
   * Get data access log
   * @param {Object} params - { limit, days }
   */
  getAccessLog(params = {}) {
    return apiClient.get('/users/privacy/access-log/', { params })
  },

  /**
   * Export all user data (GDPR)
   */
  exportData() {
    return apiClient.get('/users/privacy/export-data/')
  }
}

export default privacyAPI

