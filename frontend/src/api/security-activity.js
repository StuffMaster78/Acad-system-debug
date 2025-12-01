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
    return apiClient.get('/api/v1/users/security-activity/feed/', { params })
  },

  /**
   * Get security activity summary
   */
  getSummary() {
    return apiClient.get('/api/v1/users/security-activity/summary/')
  }
}

export default securityActivityAPI

