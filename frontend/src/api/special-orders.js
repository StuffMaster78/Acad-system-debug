import apiClient from './client'

export default {
  // Special Orders
  // Note: special-orders app is mounted under /api/v1/special-orders/, router adds /api/, then resource name
  // Full path: /api/v1/special-orders/api/special-orders/
  list: (params) => apiClient.get('/special-orders/api/special-orders/', { params }),
  get: (id) => apiClient.get(`/special-orders/api/special-orders/${id}/`),
  create: (data) => apiClient.post('/special-orders/api/special-orders/', data),
  update: (id, data) => apiClient.put(`/special-orders/api/special-orders/${id}/`, data),
  delete: (id) => apiClient.delete(`/special-orders/api/special-orders/${id}/`),
  
  // Admin Actions
  approve: (id) => apiClient.post(`/special-orders/api/special-orders/${id}/approve/`),
  overridePayment: (id) => apiClient.post(`/special-orders/api/special-orders/${id}/override_payment/`),
  completeOrder: (id) => apiClient.post(`/special-orders/api/special-orders/${id}/complete_order/`),
  assignWriter: (id, data) => apiClient.post(`/special-orders/api/special-orders/${id}/assign_writer/`, data),
  
  // Installment Payments
  listInstallments: (params) => apiClient.get('/special-orders/api/installment-payments/', { params }),
  getInstallment: (id) => apiClient.get(`/special-orders/api/installment-payments/${id}/`),
  updateInstallment: (id, data) => apiClient.put(`/special-orders/api/installment-payments/${id}/`, data),
  payInstallment: (id, data) => apiClient.post(`/special-orders/api/installment-payments/${id}/pay_installment/`, data),
  
  // Predefined Configs
  listPredefinedConfigs: (params) => apiClient.get('/special-orders/api/predefined-special-order-configs/', { params }),
  getPredefinedConfig: (id) => apiClient.get(`/special-orders/api/predefined-special-order-configs/${id}/`),
  createPredefinedConfig: (data) => apiClient.post('/special-orders/api/predefined-special-order-configs/', data),
  updatePredefinedConfig: (id, data) => apiClient.put(`/special-orders/api/predefined-special-order-configs/${id}/`, data),
  deletePredefinedConfig: (id) => apiClient.delete(`/special-orders/api/predefined-special-order-configs/${id}/`),
  
  // Predefined Durations
  listDurations: (params) => apiClient.get('/special-orders/api/predefined-special-order-durations/', { params }),
  getDuration: (id) => apiClient.get(`/special-orders/api/predefined-special-order-durations/${id}/`),
  createDuration: (data) => apiClient.post('/special-orders/api/predefined-special-order-durations/', data),
  updateDuration: (id, data) => apiClient.put(`/special-orders/api/predefined-special-order-durations/${id}/`, data),
  deleteDuration: (id) => apiClient.delete(`/special-orders/api/predefined-special-order-durations/${id}/`),
  
  // Estimated Settings
  listEstimatedSettings: (params) => apiClient.get(`/special-orders/api/estimated-special-order-settings/`, { params }),
  getEstimatedSettings: (websiteId) => apiClient.get(`/special-orders/api/estimated-special-order-settings/`, { params: { website: websiteId } }),
  updateEstimatedSettings: (id, data) => apiClient.put(`/special-orders/api/estimated-special-order-settings/${id}/`, data),
  createEstimatedSettings: (data) => apiClient.post('/special-orders/api/estimated-special-order-settings/', data),
  
  // Writer Bonuses
  listWriterBonuses: (params) => apiClient.get('/special-orders/api/writer-bonuses/', { params }),
  createWriterBonus: (data) => apiClient.post('/special-orders/api/writer-bonuses/', data),
  updateWriterBonus: (id, data) => apiClient.put(`/special-orders/api/writer-bonuses/${id}/`, data),
  deleteWriterBonus: (id) => apiClient.delete(`/special-orders/api/writer-bonuses/${id}/`),
}

