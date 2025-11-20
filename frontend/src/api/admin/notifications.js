/**
 * Admin Notification Profile Management API Service
 * 
 * This file provides API methods for managing notification profiles.
 * 
 * Usage:
 * import { notificationProfilesApi } from '@/api/admin/notifications'
 * const profiles = await notificationProfilesApi.listProfiles()
 */

import apiClient from '../client'

export const notificationProfilesApi = {
  /**
   * List all notification profiles
   * @param {Object} params - Query parameters
   * @param {string} params.search - Search by profile name
   * @returns {Promise} List of notification profiles
   */
  listProfiles: (params = {}) => {
    return apiClient.get('/admin-management/configs/notifications/', { params })
  },

  /**
   * Get a specific notification profile
   * @param {number} id - Profile ID
   * @returns {Promise} Profile details
   */
  getProfile: (id) => {
    return apiClient.get(`/admin-management/configs/notifications/${id}/`)
  },

  /**
   * Create a new notification profile
   * @param {Object} data - Profile data
   * @param {string} data.name - Profile name (required)
   * @param {string} data.description - Profile description
   * @param {number} data.website - Website ID (optional)
   * @param {boolean} data.default_email - Default email setting
   * @param {boolean} data.default_sms - Default SMS setting
   * @param {boolean} data.default_push - Default push setting
   * @param {boolean} data.default_in_app - Default in-app setting
   * @param {boolean} data.email_enabled - Email enabled
   * @param {boolean} data.sms_enabled - SMS enabled
   * @param {boolean} data.push_enabled - Push enabled
   * @param {boolean} data.in_app_enabled - In-app enabled
   * @param {boolean} data.dnd_enabled - Do-not-disturb enabled
   * @param {number} data.dnd_start_hour - DND start hour (0-23)
   * @param {number} data.dnd_end_hour - DND end hour (0-23)
   * @param {boolean} data.is_default - Whether this is the default profile
   * @returns {Promise} Created profile
   */
  createProfile: (data) => {
    return apiClient.post('/admin-management/configs/notifications/', data)
  },

  /**
   * Update a notification profile
   * @param {number} id - Profile ID
   * @param {Object} data - Updated profile data
   * @returns {Promise} Updated profile
   */
  updateProfile: (id, data) => {
    return apiClient.put(`/admin-management/configs/notifications/${id}/`, data)
  },

  /**
   * Partially update a notification profile
   * @param {number} id - Profile ID
   * @param {Object} data - Partial profile data
   * @returns {Promise} Updated profile
   */
  patchProfile: (id, data) => {
    return apiClient.patch(`/admin-management/configs/notifications/${id}/`, data)
  },

  /**
   * Delete a notification profile
   * @param {number} id - Profile ID
   * @returns {Promise} Success message
   */
  deleteProfile: (id) => {
    return apiClient.delete(`/admin-management/configs/notifications/${id}/`)
  },

  /**
   * Apply profile to a single user
   * @param {number} id - Profile ID
   * @param {Object} data - Application data
   * @param {number} data.user_id - User ID
   * @param {boolean} data.override_existing - Override existing preferences
   * @returns {Promise} Application result
   */
  applyToUser: (id, data) => {
    return apiClient.post(`/admin-management/configs/notifications/${id}/apply_to_user/`, data)
  },

  /**
   * Apply profile to multiple users
   * @param {number} id - Profile ID
   * @param {Object} data - Application data
   * @param {number[]} data.user_ids - Array of user IDs
   * @param {boolean} data.override_existing - Override existing preferences
   * @returns {Promise} Application result
   */
  applyToUsers: (id, data) => {
    return apiClient.post(`/admin-management/configs/notifications/${id}/apply_to_users/`, data)
  },

  /**
   * Get profile statistics
   * @param {number} id - Profile ID
   * @returns {Promise} Profile statistics
   */
  getStatistics: (id) => {
    return apiClient.get(`/admin-management/configs/notifications/${id}/statistics/`)
  },

  /**
   * Duplicate a profile
   * @param {number} id - Profile ID
   * @param {Object} data - Duplication data
   * @param {string} data.new_name - Name for the new profile
   * @param {number} data.website - Website ID (optional)
   * @returns {Promise} Duplicated profile
   */
  duplicateProfile: (id, data) => {
    return apiClient.post(`/admin-management/configs/notifications/${id}/duplicate/`, data)
  },

  /**
   * Get the default profile
   * @returns {Promise} Default profile
   */
  getDefaultProfile: () => {
    return apiClient.get('/admin-management/configs/notifications/default/')
  },

  /**
   * Get summary of all profiles
   * @returns {Promise} Summary statistics
   */
  getSummary: () => {
    return apiClient.get('/admin-management/configs/notifications/summary/')
  },
}

