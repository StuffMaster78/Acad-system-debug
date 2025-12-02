/**
 * Order Presets API
 * Manages reusable order presets
 */
import api from './client'

export const orderPresetsAPI = {
  /**
   * Get all order presets for current user
   * @param {Object} params - Query parameters
   */
  list(params = {}) {
    return api.get('/orders/order-presets/', { params })
  },

  /**
   * Get a specific order preset
   * @param {number} id - Preset ID
   */
  get(id) {
    return api.get(`/orders/order-presets/${id}/`)
  },

  /**
   * Create a new order preset
   * @param {Object} data - Preset data
   */
  create(data) {
    return api.post('/orders/order-presets/', data)
  },

  /**
   * Update an order preset
   * @param {number} id - Preset ID
   * @param {Object} data - Updated preset data
   */
  update(id, data) {
    return api.patch(`/orders/order-presets/${id}/`, data)
  },

  /**
   * Delete an order preset
   * @param {number} id - Preset ID
   */
  delete(id) {
    return api.delete(`/orders/order-presets/${id}/`)
  },

  /**
   * Apply preset to create a new order or draft
   * @param {number} id - Preset ID
   * @param {Object} data - Additional data for order/draft
   */
  apply(id, data = {}) {
    return api.post(`/orders/order-presets/${id}/apply/`, data)
  }
}

