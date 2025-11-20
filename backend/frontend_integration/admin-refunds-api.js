/**
 * Admin Refund Management API Service
 * 
 * This file provides API methods for the Admin Refund Management Dashboard.
 * Copy this file to your frontend project: src/api/admin/refunds.js
 * 
 * Usage:
 * import { adminRefundsApi } from '@/api/admin/refunds'
 * const dashboard = await adminRefundsApi.getDashboard()
 */

import apiClient from '../client' // Adjust import path as needed

export const adminRefundsApi = {
  /**
   * Get refund statistics dashboard
   * @returns {Promise} Dashboard data with summary and status breakdown
   */
  getDashboard: () => {
    return apiClient.get('/admin-management/refunds/dashboard/')
  },

  /**
   * Get refund analytics and trends
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to analyze (default: 30)
   * @returns {Promise} Analytics data with trends and breakdowns
   */
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/refunds/analytics/', { params })
  },

  /**
   * Get pending refunds queue
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of refunds to return (default: 50)
   * @param {string} params.status - Filter by status (optional)
   * @returns {Promise} List of pending refunds
   */
  getPendingRefunds: (params = {}) => {
    return apiClient.get('/admin-management/refunds/pending/', { params })
  },

  /**
   * Get refund history with filters
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of refunds to return (default: 50)
   * @param {string} params.status - Filter by status (optional)
   * @param {string} params.date_from - Start date (ISO format, optional)
   * @param {string} params.date_to - End date (ISO format, optional)
   * @returns {Promise} List of refunds with history
   */
  getHistory: (params = {}) => {
    return apiClient.get('/admin-management/refunds/history/', { params })
  }
}

export default adminRefundsApi

