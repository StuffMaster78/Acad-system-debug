/**
 * API client for Message Reminders
 */
import apiClient from './client'

export default {
  /**
   * Get all message reminders for the current user
   */
  list(params = {}) {
    return apiClient.get('/orders/message-reminders/', { params })
  },

  /**
   * Get a specific reminder
   */
  get(id) {
    return apiClient.get(`/orders/message-reminders/${id}/`)
  },

  /**
   * Mark message as read
   */
  markRead(id) {
    return apiClient.post(`/orders/message-reminders/${id}/mark-read/`)
  },

  /**
   * Mark message as responded
   */
  markResponded(id) {
    return apiClient.post(`/orders/message-reminders/${id}/mark-responded/`)
  },

  /**
   * Get current user's reminders
   */
  myReminders(params = {}) {
    return apiClient.get('/orders/message-reminders/my-reminders/', { params })
  },
}

