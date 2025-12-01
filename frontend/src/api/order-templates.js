import apiClient from './client'

/**
 * Order Templates API
 * Handles all order template operations
 */
export default {
  /**
   * List all order templates for the current user
   */
  list(params = {}) {
    return apiClient.get('/orders/templates/', { params })
  },

  /**
   * Get a single order template by ID
   */
  get(id) {
    return apiClient.get(`/orders/templates/${id}/`)
  },

  /**
   * Create a new order template
   */
  create(data) {
    return apiClient.post('/orders/templates/', data)
  },

  /**
   * Update an order template
   */
  update(id, data) {
    return apiClient.put(`/orders/templates/${id}/`, data)
  },

  /**
   * Partially update an order template
   */
  patch(id, data) {
    return apiClient.patch(`/orders/templates/${id}/`, data)
  },

  /**
   * Delete an order template
   */
  delete(id) {
    return apiClient.delete(`/orders/templates/${id}/`)
  },

  /**
   * Create an order from a template
   */
  createOrderFromTemplate(templateId, data = {}) {
    return apiClient.post(`/orders/templates/${templateId}/create-order/`, data)
  },

  /**
   * Get most frequently used templates
   */
  getMostUsed() {
    return apiClient.get('/orders/templates/most-used/')
  },

  /**
   * Get recently used templates
   */
  getRecent() {
    return apiClient.get('/orders/templates/recent/')
  },
}

