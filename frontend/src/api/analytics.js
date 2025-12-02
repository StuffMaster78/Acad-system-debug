/**
 * Analytics API
 * Client, writer, and class analytics
 */
import api from './client'

export const analyticsAPI = {
  /**
   * Client Analytics
   */
  client: {
    /**
     * Get all client analytics
     * @param {Object} params - Query parameters
     */
    list(params = {}) {
      return api.get('/analytics/client/', { params })
    },

    /**
     * Get specific client analytics
     * @param {number} id - Analytics ID
     */
    get(id) {
      return api.get(`/analytics/client/${id}/`)
    },

    /**
     * Get current period analytics for client
     * @param {Object} params - Query parameters (client, recalculate)
     */
    currentPeriod(params = {}) {
      return api.get('/analytics/client/current_period/', { params })
    },

    /**
     * Recalculate analytics
     * @param {number} id - Analytics ID
     */
    recalculate(id) {
      return api.post(`/analytics/client/${id}/recalculate/`)
    }
  },

  /**
   * Writer Analytics
   */
  writer: {
    /**
     * Get all writer analytics
     * @param {Object} params - Query parameters
     */
    list(params = {}) {
      return api.get('/analytics/writer/', { params })
    },

    /**
     * Get specific writer analytics
     * @param {number} id - Analytics ID
     */
    get(id) {
      return api.get(`/analytics/writer/${id}/`)
    },

    /**
     * Get current period analytics for writer
     * @param {Object} params - Query parameters (writer, recalculate)
     */
    currentPeriod(params = {}) {
      return api.get('/analytics/writer/current_period/', { params })
    },

    /**
     * Recalculate analytics
     * @param {number} id - Analytics ID
     */
    recalculate(id) {
      return api.post(`/analytics/writer/${id}/recalculate/`)
    }
  },

  /**
   * Class Analytics
   */
  class: {
    /**
     * Get all class analytics
     * @param {Object} params - Query parameters
     */
    list(params = {}) {
      return api.get('/analytics/class/', { params })
    },

    /**
     * Get specific class analytics
     * @param {number} id - Analytics ID
     */
    get(id) {
      return api.get(`/analytics/class/${id}/`)
    },

    /**
     * Create class analytics
     * @param {Object} data - Analytics data
     */
    create(data) {
      return api.post('/analytics/class/', data)
    },

    /**
     * Update class analytics
     * @param {number} id - Analytics ID
     * @param {Object} data - Updated analytics data
     */
    update(id, data) {
      return api.patch(`/analytics/class/${id}/`, data)
    },

    /**
     * Recalculate class analytics
     * @param {number} id - Analytics ID
     */
    recalculate(id) {
      return api.post(`/analytics/class/${id}/recalculate/`)
    },

    /**
     * Generate performance report
     * @param {number} id - Analytics ID
     * @param {Object} data - Report data
     */
    generateReport(id, data = {}) {
      return api.post(`/analytics/class/${id}/generate_report/`, data)
    }
  }
}

