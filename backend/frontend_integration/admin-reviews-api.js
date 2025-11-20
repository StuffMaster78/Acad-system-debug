/**
 * Admin Review Moderation API Service
 * 
 * This file provides API methods for the Admin Review Moderation Dashboard.
 * Copy this file to your frontend project: src/api/admin/reviews.js
 * 
 * Usage:
 * import { adminReviewsApi } from '@/api/admin/reviews'
 * const queue = await adminReviewsApi.getModerationQueue()
 */

import apiClient from '../client' // Adjust import path as needed

export const adminReviewsApi = {
  /**
   * Get pending reviews for moderation
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of reviews to return (default: 50)
   * @param {string} params.type - Filter by review type: 'website', 'writer', or 'order' (optional)
   * @returns {Promise} List of pending reviews with counts by type
   */
  getModerationQueue: (params = {}) => {
    return apiClient.get('/admin-management/reviews/moderation-queue/', { params })
  },

  /**
   * Approve a review
   * @param {string} reviewType - Review type: 'website', 'writer', or 'order'
   * @param {number} reviewId - Review ID
   * @returns {Promise} Approval result
   */
  approveReview: (reviewType, reviewId) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/approve/`, {
      review_type: reviewType
    })
  },

  /**
   * Reject a review
   * @param {string} reviewType - Review type: 'website', 'writer', or 'order'
   * @param {number} reviewId - Review ID
   * @param {string} reason - Reason for rejection
   * @returns {Promise} Rejection result
   */
  rejectReview: (reviewType, reviewId, reason) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/reject/`, {
      review_type: reviewType,
      reason
    })
  },

  /**
   * Flag a review for review
   * @param {string} reviewType - Review type: 'website', 'writer', or 'order'
   * @param {number} reviewId - Review ID
   * @param {string} reason - Reason for flagging
   * @returns {Promise} Flag result
   */
  flagReview: (reviewType, reviewId, reason) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/flag/`, {
      review_type: reviewType,
      reason
    })
  },

  /**
   * Shadow hide a review (hide without notifying user)
   * @param {string} reviewType - Review type: 'website', 'writer', or 'order'
   * @param {number} reviewId - Review ID
   * @returns {Promise} Shadow result
   */
  shadowReview: (reviewType, reviewId) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/shadow/`, {
      review_type: reviewType
    })
  },

  /**
   * Get review analytics dashboard
   * @returns {Promise} Analytics data with review statistics and trends
   */
  getAnalytics: () => {
    return apiClient.get('/admin-management/reviews/analytics/')
  },

  /**
   * Get spam detection alerts
   * @returns {Promise} List of potential spam reviews with detection metrics
   */
  getSpamDetection: () => {
    return apiClient.get('/admin-management/reviews/spam-detection/')
  }
}

export default adminReviewsApi

