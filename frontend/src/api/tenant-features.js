/**
 * Tenant Features API
 * Branding and feature toggles
 */
import api from './client'

export const tenantFeaturesAPI = {
  /**
   * Tenant Branding
   */
  branding: {
    /**
     * Get all branding configurations
     * @param {Object} params - Query parameters
     */
    list(params = {}) {
      return api.get('/websites/branding/', { params })
    },

    /**
     * Get current branding for user's website
     */
    getCurrent() {
      return api.get('/websites/branding/current/')
    },

    /**
     * Get specific branding
     * @param {number} id - Branding ID
     */
    get(id) {
      return api.get(`/websites/branding/${id}/`)
    },

    /**
     * Create branding configuration
     * @param {Object} data - Branding data
     */
    create(data) {
      return api.post('/websites/branding/', data)
    },

    /**
     * Update branding configuration
     * @param {number} id - Branding ID
     * @param {Object} data - Updated branding data
     */
    update(id, data) {
      return api.patch(`/websites/branding/${id}/`, data)
    }
  },

  /**
   * Feature Toggles
   */
  toggles: {
    /**
     * Get all feature toggles
     * @param {Object} params - Query parameters
     */
    list(params = {}) {
      return api.get('/websites/feature-toggles/', { params })
    },

    /**
     * Get current feature toggles for user's website
     */
    getCurrent() {
      return api.get('/websites/feature-toggles/current/')
    },

    /**
     * Get specific feature toggle
     * @param {number} id - Toggle ID
     */
    get(id) {
      return api.get(`/websites/feature-toggles/${id}/`)
    },

    /**
     * Create feature toggle
     * @param {Object} data - Toggle data
     */
    create(data) {
      return api.post('/websites/feature-toggles/', data)
    },

    /**
     * Update feature toggle
     * @param {number} id - Toggle ID
     * @param {Object} data - Updated toggle data
     */
    update(id, data) {
      return api.patch(`/websites/feature-toggles/${id}/`, data)
    },

    /**
     * Check if a specific feature is enabled
     * @param {number} id - Toggle ID
     * @param {string} feature - Feature name
     */
    checkFeature(id, feature) {
      return api.get(`/websites/feature-toggles/${id}/check_feature/`, {
        params: { feature }
      })
    }
  }
}

