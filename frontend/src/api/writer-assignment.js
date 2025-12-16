import apiClient from './client'

const writerAssignmentAPI = {
  /**
   * Get available writers with workload details for assignment
   * @param {number} orderId - Optional order ID to get writers suitable for that order
   * @returns {Promise} API response with writers list and their workload
   */
  getAvailableWriters: (orderId = null) => {
    const params = orderId ? { order_id: orderId } : {}
    return apiClient.get('/admin-management/writer-assignment/available-writers/', { params })
  },

  /**
   * Get detailed workload information for a specific writer
   * @param {number} writerId - The writer ID
   * @returns {Promise} API response with writer workload details
   */
  getWriterWorkload: (writerId) => {
    return apiClient.get(`/admin-management/writer-assignment/${writerId}/workload/`)
  },

  // Writer Assignment Acceptance endpoints
  /**
   * List all assignment acceptances (writers see only their own, admins see all)
   * @param {object} params - Query parameters
   * @returns {Promise} API response with assignment acceptances list
   */
  listAcceptances: (params = {}) => {
    return apiClient.get('/orders/writer-assignment-acceptances/', { params })
  },

  /**
   * Get a specific assignment acceptance by ID
   * @param {number} id - Assignment acceptance ID
   * @returns {Promise} API response with assignment acceptance details
   */
  getAcceptance: (id) => {
    return apiClient.get(`/orders/writer-assignment-acceptances/${id}/`)
  },

  /**
   * Get all pending assignments for the current writer
   * @returns {Promise} API response with pending assignments list
   */
  getPendingAssignments: () => {
    return apiClient.get('/orders/writer-assignment-acceptances/pending/')
  },

  /**
   * Accept an assignment
   * @param {number} id - Assignment acceptance ID
   * @param {string} reason - Optional reason for accepting
   * @returns {Promise} API response
   */
  acceptAssignment: (id, reason = '') => {
    return apiClient.post(`/orders/writer-assignment-acceptances/${id}/accept/`, { reason })
  },

  /**
   * Reject an assignment
   * @param {number} id - Assignment acceptance ID
   * @param {string} reason - Optional reason for rejecting
   * @returns {Promise} API response
   */
  rejectAssignment: (id, reason = '') => {
    return apiClient.post(`/orders/writer-assignment-acceptances/${id}/reject/`, { reason })
  },

  // Preferred Writer Response endpoints
  /**
   * Get all pending preferred writer assignments for the current writer
   * @returns {Promise} API response with pending preferred assignments list
   */
  getPendingPreferredAssignments: () => {
    return apiClient.get('/orders/preferred-writer-responses/pending/')
  },

  /**
   * Accept a preferred writer assignment
   * @param {number} orderId - Order ID
   * @returns {Promise} API response
   */
  acceptPreferredAssignment: (orderId) => {
    return apiClient.post(`/orders/preferred-writer-responses/${orderId}/accept/`)
  },

  /**
   * Reject a preferred writer assignment
   * @param {number} orderId - Order ID
   * @param {string} reason - Optional reason for rejecting
   * @returns {Promise} API response
   */
  rejectPreferredAssignment: (orderId, reason = '') => {
    return apiClient.post(`/orders/preferred-writer-responses/${orderId}/reject/`, { reason })
  },
}

export default writerAssignmentAPI

