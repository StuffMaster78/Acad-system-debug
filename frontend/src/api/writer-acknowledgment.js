/**
 * API client for Writer Assignment Acknowledgment
 */
import apiClient from './client'

export default {
  /**
   * Get all acknowledgments for the current user
   */
  list(params = {}) {
    return apiClient.get('/orders/writer-acknowledgments/', { params })
  },

  /**
   * Get a specific acknowledgment
   */
  get(id) {
    return apiClient.get(`/orders/writer-acknowledgments/${id}/`)
  },

  /**
   * Acknowledge assignment to an order
   */
  acknowledge(orderId) {
    return apiClient.post(`/orders/writer-acknowledgments/acknowledge/${orderId}/`)
  },

  /**
   * Mark that message was sent
   */
  markMessageSent(id) {
    return apiClient.post(`/orders/writer-acknowledgments/${id}/mark-message-sent/`)
  },

  /**
   * Mark that files were downloaded
   */
  markFileDownloaded(id) {
    return apiClient.post(`/orders/writer-acknowledgments/${id}/mark-file-downloaded/`)
  },

  /**
   * Get current user's acknowledgments
   */
  myAcknowledgments(params = {}) {
    return apiClient.get('/orders/writer-acknowledgments/my-acknowledgments/', { params })
  },
}

