/**
 * Writer Capacity API
 * Manages writer capacity and availability
 */
import api from './client'

export const writerCapacityAPI = {
  /**
   * Get writer capacity settings
   * @param {Object} params - Query parameters
   */
  list(params = {}) {
    return api.get('/writer-management/capacity/', { params })
  },

  /**
   * Get specific writer capacity
   * @param {number} id - Capacity ID
   */
  get(id) {
    return api.get(`/writer-management/capacity/${id}/`)
  },

  /**
   * Create or update writer capacity
   * @param {Object} data - Capacity data
   */
  create(data) {
    return api.post('/writer-management/capacity/', data)
  },

  /**
   * Update writer capacity
   * @param {number} id - Capacity ID
   * @param {Object} data - Updated capacity data
   */
  update(id, data) {
    return api.patch(`/writer-management/capacity/${id}/`, data)
  },

  /**
   * Editor Workload
   */
  editor: {
    /**
     * Get editor workload settings
     * @param {Object} params - Query parameters
     */
    list(params = {}) {
      return api.get('/writer-management/editor-workload/', { params })
    },

    /**
     * Get specific editor workload
     * @param {number} id - Workload ID
     */
    get(id) {
      return api.get(`/writer-management/editor-workload/${id}/`)
    },

    /**
     * Create or update editor workload
     * @param {Object} data - Workload data
     */
    create(data) {
      return api.post('/writer-management/editor-workload/', data)
    },

    /**
     * Update editor workload
     * @param {number} id - Workload ID
     * @param {Object} data - Updated workload data
     */
    update(id, data) {
      return api.patch(`/writer-management/editor-workload/${id}/`, data)
    }
  }
}

