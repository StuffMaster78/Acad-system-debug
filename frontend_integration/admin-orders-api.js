/**
 * Admin Orders Management API Service
 * 
 * This file provides API methods for the Admin Order Management Dashboard.
 * Copy this file to your frontend project: src/api/admin/orders.js
 * 
 * Usage:
 * import { adminOrdersApi } from '@/api/admin/orders'
 * const dashboard = await adminOrdersApi.getDashboard()
 */

import apiClient from '../client' // Adjust import path as needed

export const adminOrdersApi = {
  /**
   * Get order statistics dashboard
   * @returns {Promise} Dashboard data with summary, status breakdown, and weekly trends
   */
  getDashboard: () => {
    return apiClient.get('/admin-management/orders/dashboard/')
  },

  /**
   * Get order analytics and trends
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to analyze (default: 30)
   * @returns {Promise} Analytics data with monthly/weekly trends, service breakdown, etc.
   */
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/orders/analytics/', { params })
  },

  /**
   * Get orders needing assignment
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of orders to return (default: 50)
   * @param {string} params.status - Filter by status (optional)
   * @returns {Promise} List of orders needing assignment
   */
  getAssignmentQueue: (params = {}) => {
    return apiClient.get('/admin-management/orders/assignment-queue/', { params })
  },

  /**
   * Get overdue orders
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of orders to return (default: 50)
   * @returns {Promise} List of overdue orders
   */
  getOverdueOrders: (params = {}) => {
    return apiClient.get('/admin-management/orders/overdue/', { params })
  },

  /**
   * Get stuck orders (no progress for extended period)
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of orders to return (default: 50)
   * @param {number} params.days - Days threshold for stuck orders (default: 7)
   * @returns {Promise} List of stuck orders
   */
  getStuckOrders: (params = {}) => {
    return apiClient.get('/admin-management/orders/stuck/', { params })
  },

  /**
   * Bulk assign orders to writers
   * @param {Object} data - Assignment data
   * @param {number[]} data.order_ids - Array of order IDs to assign
   * @param {number} data.writer_id - Writer ID to assign to
   * @param {string} data.reason - Reason for assignment (optional)
   * @returns {Promise} Assignment results with success/failed arrays
   */
  bulkAssign: (data) => {
    return apiClient.post('/admin-management/orders/bulk-assign/', data)
  },

  /**
   * Perform bulk actions on orders
   * @param {Object} data - Action data
   * @param {number[]} data.order_ids - Array of order IDs
   * @param {string} data.action - Action to perform: 'cancel', 'refund', 'archive', 'on_hold'
   * @param {string} data.notes - Optional notes
   * @returns {Promise} Action results with success/failed arrays
   */
  bulkAction: (data) => {
    return apiClient.post('/admin-management/orders/bulk-action/', data)
  },

  /**
   * Get order timeline/history
   * @param {number} orderId - Order ID
   * @returns {Promise} Order details with complete timeline of events
   */
  getOrderTimeline: (orderId) => {
    return apiClient.get(`/admin-management/orders/${orderId}/timeline/`)
  }
}

export default adminOrdersApi

