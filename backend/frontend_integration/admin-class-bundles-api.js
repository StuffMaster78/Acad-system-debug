/**
 * Admin Class Bundles Management API Service
 * 
 * This file provides API methods for the Admin Class Bundles Management Dashboard.
 * Copy this file to your frontend project: src/api/admin/classBundles.js
 * 
 * Usage:
 * import { adminClassBundlesApi } from '@/api/admin/classBundles'
 * const dashboard = await adminClassBundlesApi.getDashboard()
 */

import apiClient from '../client' // Adjust import path as needed

export const adminClassBundlesApi = {
  /**
   * Get class bundle statistics dashboard
   * @returns {Promise} Dashboard data with summary, status breakdown, and level breakdown
   */
  getDashboard: () => {
    return apiClient.get('/admin-management/class-bundles/dashboard/')
  },

  /**
   * Get installment payment tracking
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of installments to return (default: 50)
   * @param {string} params.status - Filter by status: 'paid', 'unpaid', or 'overdue' (optional)
   * @returns {Promise} List of installments with statistics
   */
  getInstallmentTracking: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/installment-tracking/', { params })
  },

  /**
   * Get bundles with pending deposits
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of bundles to return (default: 50)
   * @returns {Promise} List of bundles with pending deposits
   */
  getDepositPending: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/deposit-pending/', { params })
  },

  /**
   * Get class bundle analytics and trends
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to analyze (default: 30)
   * @returns {Promise} Analytics data with monthly/weekly trends, level breakdown, etc.
   */
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/analytics/', { params })
  },

  /**
   * Get predefined bundle configurations
   * @returns {Promise} List of bundle configs with durations
   */
  getConfigs: () => {
    return apiClient.get('/admin-management/class-bundles/configs/')
  },

  /**
   * Create or update bundle configuration
   * @param {Object} data - Config data
   * @param {number} data.id - Config ID for update (optional, omit for create)
   * @param {number} data.website - Website ID
   * @param {number} data.duration - Duration option ID
   * @param {string} data.level - Level: 'undergrad' or 'grad'
   * @param {number} data.bundle_size - Number of classes in bundle
   * @param {number} data.price_per_class - Price per class
   * @param {boolean} data.is_active - Whether config is active (default: true)
   * @returns {Promise} Created/updated config data
   */
  createOrUpdateConfig: (data) => {
    return apiClient.post('/admin-management/class-bundles/configs/', data)
  },

  /**
   * Get communication threads for class bundles
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of threads to return (default: 50)
   * @param {number} params.bundle_id - Filter by bundle ID (optional)
   * @returns {Promise} List of communication threads with bundle info
   */
  getCommunicationThreads: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/communication-threads/', { params })
  },

  /**
   * Get support tickets for class bundles
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of tickets to return (default: 50)
   * @param {number} params.bundle_id - Filter by bundle ID (optional)
   * @param {string} params.status - Filter by ticket status (optional)
   * @returns {Promise} List of support tickets with bundle info
   */
  getSupportTickets: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/support-tickets/', { params })
  }
}

export default adminClassBundlesApi

