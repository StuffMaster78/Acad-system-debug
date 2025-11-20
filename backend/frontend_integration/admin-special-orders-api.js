/**
 * Admin Special Orders Management API Service
 * 
 * This file provides API methods for the Admin Special Orders Management Dashboard.
 * Copy this file to your frontend project: src/api/admin/specialOrders.js
 * 
 * Usage:
 * import { adminSpecialOrdersApi } from '@/api/admin/specialOrders'
 * const dashboard = await adminSpecialOrdersApi.getDashboard()
 */

import apiClient from '../client' // Adjust import path as needed

export const adminSpecialOrdersApi = {
  /**
   * Get special order statistics dashboard
   * @returns {Promise} Dashboard data with summary, status breakdown, and type breakdown
   */
  getDashboard: () => {
    return apiClient.get('/admin-management/special-orders/dashboard/')
  },

  /**
   * Get orders awaiting approval
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of orders to return (default: 50)
   * @param {string} params.status - Filter by status: 'inquiry' or 'awaiting_approval' (optional)
   * @param {string} params.order_type - Filter by order type: 'predefined' or 'estimated' (optional)
   * @returns {Promise} List of orders awaiting approval
   */
  getApprovalQueue: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/approval-queue/', { params })
  },

  /**
   * Get orders needing cost estimation
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of orders to return (default: 50)
   * @returns {Promise} List of orders needing cost estimation
   */
  getEstimatedQueue: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/estimated-queue/', { params })
  },

  /**
   * Get installment payment tracking
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of installments to return (default: 50)
   * @param {string} params.status - Filter by status: 'paid', 'unpaid', or 'overdue' (optional)
   * @returns {Promise} List of installments with statistics
   */
  getInstallmentTracking: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/installment-tracking/', { params })
  },

  /**
   * Get special order analytics and trends
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to analyze (default: 30)
   * @returns {Promise} Analytics data with monthly/weekly trends, type breakdown, etc.
   */
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/analytics/', { params })
  },

  /**
   * Get predefined order configurations
   * @returns {Promise} List of predefined order configs with durations
   */
  getConfigs: () => {
    return apiClient.get('/admin-management/special-orders/configs/')
  },

  /**
   * Create or update predefined order configuration
   * @param {Object} data - Config data
   * @param {number} data.id - Config ID for update (optional, omit for create)
   * @param {string} data.name - Config name
   * @param {string} data.description - Config description (optional)
   * @param {number} data.website - Website ID
   * @param {boolean} data.is_active - Whether config is active (default: true)
   * @param {Array} data.durations - Array of duration objects: [{duration_days: number, price: number}]
   * @returns {Promise} Created/updated config data
   */
  createOrUpdateConfig: (data) => {
    return apiClient.post('/admin-management/special-orders/configs/', data)
  }
}

export default adminSpecialOrdersApi

