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
}

export default writerAssignmentAPI

