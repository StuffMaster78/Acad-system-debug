/**
 * Order Drafts API
 * Manages order drafts and quotes
 */
import api from './client'

export const orderDraftsAPI = {
  /**
   * Get all order drafts for current user
   * @param {Object} params - Query parameters
   */
  list(params = {}) {
    return api.get('/orders/order-drafts/', { params })
  },

  /**
   * Get a specific order draft
   * @param {number} id - Draft ID
   */
  get(id) {
    return api.get(`/orders/order-drafts/${id}/`)
  },

  /**
   * Create a new order draft
   * @param {Object} data - Draft data
   */
  create(data) {
    return api.post('/orders/order-drafts/', data)
  },

  /**
   * Update an order draft
   * @param {number} id - Draft ID
   * @param {Object} data - Updated draft data
   */
  update(id, data) {
    return api.patch(`/orders/order-drafts/${id}/`, data)
  },

  /**
   * Delete an order draft
   * @param {number} id - Draft ID
   */
  delete(id) {
    return api.delete(`/orders/order-drafts/${id}/`)
  },

  /**
   * Get quote/calculate price for draft
   * @param {number} id - Draft ID
   */
  getQuote(id) {
    return api.post(`/orders/order-drafts/${id}/calculate-price/`)
  },

  /**
   * Convert draft to order
   * @param {number} id - Draft ID
   * @param {Object} data - Additional order data
   */
  convertToOrder(id, data = {}) {
    return api.post(`/orders/order-drafts/${id}/convert-to-order/`, data)
  }
}

