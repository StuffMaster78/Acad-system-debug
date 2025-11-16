/**
 * Admin Dispute Management API Service
 * 
 * This file provides API methods for the Admin Dispute Management Dashboard.
 * Copy this file to your frontend project: src/api/admin/disputes.js
 * 
 * Usage:
 * import { adminDisputesApi } from '@/api/admin/disputes'
 * const dashboard = await adminDisputesApi.getDashboard()
 */

import apiClient from '../client' // Adjust import path as needed

export const adminDisputesApi = {
  /**
   * Get dispute statistics dashboard
   * @returns {Promise} Dashboard data with summary and status breakdown
   */
  getDashboard: () => {
    return apiClient.get('/admin-management/disputes/dashboard/')
  },

  /**
   * Get dispute analytics and trends
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to analyze (default: 30)
   * @returns {Promise} Analytics data with trends and breakdowns
   */
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/disputes/analytics/', { params })
  },

  /**
   * Get pending disputes queue
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of disputes to return (default: 50)
   * @param {string} params.status - Filter by status (optional)
   * @returns {Promise} List of pending disputes
   */
  getPendingDisputes: (params = {}) => {
    return apiClient.get('/admin-management/disputes/pending/', { params })
  },

  /**
   * Bulk resolve disputes
   * @param {Object} data - Resolution data
   * @param {number[]} data.dispute_ids - Array of dispute IDs
   * @param {string} data.resolution - Resolution outcome
   * @param {string} data.notes - Optional notes
   * @returns {Promise} Resolution results with success/failed arrays
   */
  bulkResolve: (data) => {
    return apiClient.post('/admin-management/disputes/bulk-resolve/', data)
  }
}

export default adminDisputesApi

