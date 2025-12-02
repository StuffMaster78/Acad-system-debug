/**
 * Security Activity API - Security events and activity monitoring
 */
import apiClient from './client'

const securityActivityAPI = {
  /**
   * Get security activity feed
   * @param {Object} params - { limit, days, event_type, suspicious_only }
   */
  getActivityFeed(params = {}) {
    // Remove duplicate /api/v1/ prefix as apiClient already includes it
    return apiClient.get('/users/security-activity/feed/', { params })
  },

  /**
   * Get security activity summary
   */
  getSummary() {
    // Remove duplicate /api/v1/ prefix as apiClient already includes it
    return apiClient.get('/users/security-activity/summary/')
  }
}

export default securityActivityAPI

