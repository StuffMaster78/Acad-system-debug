import apiClient from './client'

export default {
  // Note: orders app is mounted under /api/v1/orders/, and the resource is /orders/
  list: (params) => apiClient.get('/orders/orders/', { params }),
  get: (id) => apiClient.get(`/orders/orders/${id}/`),
  createClient: (data) => apiClient.post('/orders/orders/create/', data),
  quote: (data) => apiClient.post('/orders/orders/quote/', data),
  update: (id, data) => apiClient.put(`/orders/orders/${id}/`, data),
  patch: (id, data) => apiClient.patch(`/orders/orders/${id}/`, data),
  delete: (id) => apiClient.delete(`/orders/orders/${id}/`),
  payWithWallet: (id) => apiClient.post(`/orders/orders/${id}/pay/wallet/`),
  getPreferredWriters: () => apiClient.get('/orders/orders/preferred-writers/'),
  getPaymentSummary: (id) => apiClient.get(`/orders/orders/${id}/payment-summary/`),
  
  // Order Actions
  getAvailableActions: (id) => apiClient.get(`/orders/orders/${id}/action/`),
  executeAction: (id, action, params = {}) => apiClient.post(`/orders/orders/${id}/action/`, { action, ...params }),
  assignWriter: (id, writerId, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'assign_writer', writer_id: writerId, reason }),
  reassignWriter: (id, writerId, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'reassign_writer', writer_id: writerId, reason }),
  approveOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'approve_order' }),
  cancelOrder: (id, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'cancel_order', reason }),
  completeOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'complete_order' }),
  holdOrder: (id, reason = '') => apiClient.post(`/orders/orders/${id}/action/`, { action: 'hold_order', reason }),
  resumeOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'resume_order' }),
  archiveOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'archive_order' }),
  reopenOrder: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'reopen_order' }),
  markCritical: (id) => apiClient.post(`/orders/orders/${id}/action/`, { action: 'mark_critical' }),
  extendDeadline: (id, newDeadline) => apiClient.post(`/orders/orders/${id}/extend-deadline/`, { new_deadline: newDeadline }),
}

