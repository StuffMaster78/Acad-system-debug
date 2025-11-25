import apiClient from './client'

export default {
  // Writer Order Requests
  list: (params) => apiClient.get('/writer-management/writer-order-requests/', { params }),
  get: (id) => apiClient.get(`/writer-management/writer-order-requests/${id}/`),
  create: (data) => apiClient.post('/writer-management/writer-order-requests/', data),
  update: (id, data) => apiClient.patch(`/writer-management/writer-order-requests/${id}/`, data),
  delete: (id) => apiClient.delete(`/writer-management/writer-order-requests/${id}/`),
  
  // Writer Order Takes (if enabled)
  listTakes: (params) => apiClient.get('/writer-management/writer-order-takes/', { params }),
  createTake: (data) => apiClient.post('/writer-management/writer-order-takes/', data),
}

