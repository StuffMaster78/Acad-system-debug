/**
 * API client for Review Reminders
 */
import apiClient from './client'

export default {
  /**
   * Get all review reminders for the current user
   */
  list(params = {}) {
    return apiClient.get('/orders/review-reminders/', { params })
  },

  /**
   * Get a specific reminder
   */
  get(id) {
    return apiClient.get(`/orders/review-reminders/${id}/`)
  },

  /**
   * Mark as reviewed
   */
  markReviewed(id) {
    return apiClient.post(`/orders/review-reminders/${id}/mark-reviewed/`)
  },

  /**
   * Mark as rated
   */
  markRated(id, rating) {
    return apiClient.post(`/orders/review-reminders/${id}/mark-rated/`, { rating })
  },

  /**
   * Get current user's reminders
   */
  myReminders(params = {}) {
    return apiClient.get('/orders/review-reminders/my-reminders/', { params })
  },
}

