import apiClient from './client'

export default {
  // Note: orders app is mounted under /api/v1/orders/, and the resource is /orders/
  list: (params) => apiClient.get('/orders/orders/', { params }),
  getFilterMetadata: () => apiClient.get('/orders/orders/filter-options/'),
  get: (id) => apiClient.get(`/orders/orders/${id}/`),
  createClient: (data) => apiClient.post('/orders/orders/create/', data),
  quote: (data) => apiClient.post('/orders/orders/quote/', data),
  update: (id, data) => apiClient.put(`/orders/orders/${id}/`, data),
  patch: (id, data) => apiClient.patch(`/orders/orders/${id}/`, data),
  delete: (id) => apiClient.delete(`/orders/orders/${id}/`),
  payWithWallet: (id) => apiClient.post(`/orders/orders/${id}/pay/wallet/`),
  getPreferredWriters: () => apiClient.get('/orders/orders/preferred-writers/'),
  getPaymentSummary: (id) => apiClient.get(`/orders/orders/${id}/payment-summary/`),
  addPagesSlides: (id, data) => apiClient.post(`/orders/orders/${id}/add-pages-slides/`, data),
  addExtraServices: (id, data) => apiClient.post(`/orders/orders/${id}/add-extra-services/`, data),
  
  // Order Actions
  getAvailableActions: (id) => apiClient.get(`/orders/orders/${id}/action/`),
  executeAction: (id, action, params = {}) => apiClient.post(`/orders/orders/${id}/action/`, { action, ...params }),
  assignWriter: (id, writerId, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'assign_order', writer_id: writerId, reason }),
  reassignWriter: (id, writerId, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'reassign_order', writer_id: writerId, reason }),
  approveOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'approve_order' }),
  cancelOrder: (id, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'cancel_order', reason }),
  completeOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'complete_order' }),
  holdOrder: (id, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'hold_order', reason }),
  resumeOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'resume_order' }),
  archiveOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'archive_order' }),
  
  // Guest Checkout
  startGuestOrder: (data) => apiClient.post('/orders/guest-orders/start/', data),
  verifyGuestEmail: (data) => apiClient.post('/orders/guest-orders/verify-email/', data),
  reopenOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'reopen_order' }),
  markCritical: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'mark_critical' }),
  extendDeadline: (id, newDeadline) => apiClient.post(`/orders/orders/${id}/extend-deadline/`, { new_deadline: newDeadline }),
  
  // Writer Requests (additional pages/slides)
  createWriterRequest: (orderId, data) => apiClient.post(`/orders/writer-requests/`, { order: orderId, ...data }),
  getWriterRequests: (orderId) => apiClient.get(`/orders/orders/${orderId}/writer-requests/`),
  approveWriterRequest: (orderId, requestId, data) => apiClient.post(`/orders/orders/${orderId}/approve-writer-request/`, { writer_request_id: requestId, ...data }),
  
  // Client response to writer requests
  clientRespondToWriterRequest: (orderId, requestId, data) => apiClient.post(`/orders/orders/${orderId}/action/`, {
    action: 'client_respond_writer_request',
    request_id: requestId,
    ...data
  }),
  
  // Soft Delete & Restore
  softDelete: (id, reason = '') => apiClient.delete(`/orders/orders/${id}/`, { data: { reason } }),
  restore: (id) => apiClient.post(`/orders/orders/${id}/restore/`),
  
  // Auto-Assignment
  autoAssign: (id, data = {}) => apiClient.post(`/orders/orders/${id}/auto-assign/`, data),
  bulkAutoAssign: (data = {}) => apiClient.post('/orders/orders/bulk-auto-assign/', data),
  
  // Bulk Assignment
  bulkAssign: (data = {}) => apiClient.post('/orders/orders/bulk-assign/', data),
  
  // Smart Matching
  getSmartMatches: (id, params = {}) => apiClient.get(`/orders/orders/${id}/smart-match/`, { params }),
  hardDelete: (id) => apiClient.delete(`/orders/orders/${id}/hard/`),
  
  // Unified Transition Endpoint (preferred method)
  /**
   * Transition an order to a new status using the unified transition endpoint.
   * This is the preferred method for status transitions as it provides:
   * - Consistent validation
   * - Automatic logging
   * - Business rule enforcement
   * 
   * @param {number} id - Order ID
   * @param {string} targetStatus - Target status (e.g., 'in_progress', 'submitted', 'completed')
   * @param {string} reason - Optional reason for the transition
   * @param {object} metadata - Optional additional metadata
   * @returns {Promise} API response
   */
  transition: (id, targetStatus, reason = '', metadata = {}) => 
    apiClient.post(`/orders/orders/${id}/transition/`, {
      target_status: targetStatus,
      reason,
      ...metadata
    }),
  
  /**
   * Get available transitions for an order.
   * @param {number} id - Order ID
   * @returns {Promise} API response with available transitions
   */
  getAvailableTransitions: (id) => 
    apiClient.get(`/orders/orders/${id}/transition/`),

  /**
   * Get transition log entries for an order (admin only).
   * @param {number} id - Order ID
   */
  getTransitionLog: (id) =>
    apiClient.get('/orders/logs/', { params: { order: id } }),
}

