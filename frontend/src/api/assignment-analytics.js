import apiClient from './client'

/**
 * API client for Assignment Analytics endpoints
 */
export default {
  /**
   * Get comprehensive assignment analytics dashboard
   * @param {Object} params - Query parameters (website_id, start_date, end_date)
   * @returns {Promise} API response with dashboard data
   */
  getDashboard: (params = {}) => apiClient.get('/orders/assignment-analytics/dashboard/', { params }),

  /**
   * Get assignment success rates
   * @param {Object} params - Query parameters (website_id, start_date, end_date)
   * @returns {Promise} API response with success rate metrics
   */
  getSuccessRates: (params = {}) => apiClient.get('/orders/assignment-analytics/success-rates/', { params }),

  /**
   * Get average acceptance times
   * @param {Object} params - Query parameters (website_id, start_date, end_date)
   * @returns {Promise} API response with acceptance time metrics
   */
  getAcceptanceTimes: (params = {}) => apiClient.get('/orders/assignment-analytics/acceptance-times/', { params }),

  /**
   * Get rejection reasons and frequencies
   * @param {Object} params - Query parameters (website_id, start_date, end_date, limit)
   * @returns {Promise} API response with rejection reasons
   */
  getRejectionReasons: (params = {}) => apiClient.get('/orders/assignment-analytics/rejection-reasons/', { params }),

  /**
   * Get writer performance metrics
   * @param {Object} params - Query parameters (writer_id, website_id, start_date, end_date)
   * @returns {Promise} API response with writer performance data
   */
  getWriterPerformance: (params = {}) => apiClient.get('/orders/assignment-analytics/writer-performance/', { params }),

  /**
   * Get assignment trends over time
   * @param {Object} params - Query parameters (website_id, start_date, end_date, group_by)
   * @returns {Promise} API response with trend data
   */
  getTrends: (params = {}) => apiClient.get('/orders/assignment-analytics/trends/', { params }),
}

