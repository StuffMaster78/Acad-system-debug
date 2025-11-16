/**
 * Admin Tip Management API Service
 * 
 * This file provides API methods for the Admin Tip Management Dashboard.
 * Copy this file to your frontend project: src/api/admin/tips.js
 * 
 * Usage:
 * import { adminTipsApi } from '@/api/admin/tips'
 * const dashboard = await adminTipsApi.getDashboard()
 */

import apiClient from '../client' // Adjust import path as needed

export const adminTipsApi = {
  /**
   * Get tip statistics dashboard with earnings breakdown
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days for recent summary (default: 30)
   * @returns {Promise} Dashboard data with summary, recent summary, payment status, and breakdowns
   */
  getDashboard: (params = {}) => {
    return apiClient.get('/admin-management/tips/dashboard/', { params })
  },

  /**
   * List all tips with earnings breakdown
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of tips to return (default: 50)
   * @param {number} params.offset - Offset for pagination (default: 0)
   * @param {string} params.tip_type - Filter by tip type: 'direct', 'order', or 'class' (optional)
   * @param {string} params.payment_status - Filter by payment status: 'pending', 'processing', 'completed', 'failed' (optional)
   * @param {number} params.writer_id - Filter by writer ID (optional)
   * @param {number} params.client_id - Filter by client ID (optional)
   * @param {string} params.date_from - Filter from date (ISO format) (optional)
   * @param {string} params.date_to - Filter to date (ISO format) (optional)
   * @returns {Promise} List of tips with summary statistics
   */
  listTips: (params = {}) => {
    return apiClient.get('/admin-management/tips/list_tips/', { params })
  },

  /**
   * Get tip analytics with trends and breakdowns
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to analyze (default: 90)
   * @returns {Promise} Analytics data with trends, breakdowns, and top performers
   */
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/tips/analytics/', { params })
  },

  /**
   * Get detailed earnings breakdown
   * @param {Object} params - Query parameters
   * @param {string} params.date_from - Filter from date (ISO format) (optional)
   * @param {string} params.date_to - Filter to date (ISO format) (optional)
   * @returns {Promise} Earnings data with overall stats, breakdowns by level/type, and monthly trends
   */
  getEarnings: (params = {}) => {
    return apiClient.get('/admin-management/tips/earnings/', { params })
  },
}

export default adminTipsApi

