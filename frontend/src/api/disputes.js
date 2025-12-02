/**
 * Enhanced Disputes API
 * Enhanced dispute management with escalation and resolution
 */
import api from './client'

export const disputesAPI = {
  /**
   * Get all disputes
   * @param {Object} params - Query parameters (status, priority, order)
   */
  list(params = {}) {
    return api.get('/support-management/disputes/', { params })
  },

  /**
   * Get a specific dispute
   * @param {number} id - Dispute ID
   */
  get(id) {
    return api.get(`/support-management/disputes/${id}/`)
  },

  /**
   * Create a new dispute
   * @param {Object} data - Dispute data
   */
  create(data) {
    return api.post('/support-management/disputes/', data)
  },

  /**
   * Update a dispute
   * @param {number} id - Dispute ID
   * @param {Object} data - Updated dispute data
   */
  update(id, data) {
    return api.patch(`/support-management/disputes/${id}/`, data)
  },

  /**
   * Escalate dispute
   * @param {number} id - Dispute ID
   * @param {Object} data - Escalation data
   */
  escalate(id, data) {
    return api.post(`/support-management/disputes/${id}/escalate/`, data)
  },

  /**
   * Resolve dispute
   * @param {number} id - Dispute ID
   * @param {Object} data - Resolution data
   */
  resolve(id, data) {
    return api.post(`/support-management/disputes/${id}/resolve/`, data)
  },

  /**
   * Close dispute
   * @param {number} id - Dispute ID
   */
  close(id) {
    return api.post(`/support-management/disputes/${id}/close/`)
  },

  /**
   * Dispute Messages
   */
  messages: {
    /**
     * Get messages for a dispute
     * @param {number} disputeId - Dispute ID
     * @param {Object} params - Query parameters
     */
    list(disputeId, params = {}) {
      return api.get('/support-management/dispute-messages/', {
        params: { dispute: disputeId, ...params }
      })
    },

    /**
     * Create a message in a dispute
     * @param {Object} data - Message data
     */
    create(data) {
      return api.post('/support-management/dispute-messages/', data)
    }
  }
}

export default disputesAPI
