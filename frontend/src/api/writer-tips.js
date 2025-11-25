import apiClient from './client'

export default {
  // Tips - Full CRUD support
  list: (params) => apiClient.get('/writer-management/tips/', { params }),
  get: (id) => apiClient.get(`/writer-management/tips/${id}/`),
  create: (data) => apiClient.post('/writer-management/tips/', data),
  
  // Filter tips
  getByType: (tipType, params = {}) => apiClient.get('/writer-management/tips/', { 
    params: { tip_type: tipType, ...params } 
  }),
  getByOrder: (orderId, params = {}) => apiClient.get('/writer-management/tips/', { 
    params: { order_id: orderId, ...params } 
  }),
  getByClass: (entityType, entityId, params = {}) => apiClient.get('/writer-management/tips/', { 
    params: { related_entity_type: entityType, related_entity_id: entityId, ...params } 
  }),
  
  // Process payment for a tip
  processPayment: (tipId, data) => apiClient.post(`/writer-management/tips/${tipId}/process_payment/`, data),
  
  // Tips statistics (if endpoint exists)
  getStats: () => apiClient.get('/writer-management/tips/stats/'),
}

