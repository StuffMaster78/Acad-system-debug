import apiClient from './client'

export default {
  // Order Disputes
  list: (params) => apiClient.get('/orders/disputes/', { params }),
  get: (id) => apiClient.get(`/orders/disputes/${id}/`),
  create: (data) => apiClient.post('/orders/disputes/', data),
  resolve: (id, data) => apiClient.post(`/orders/disputes/${id}/resolve_dispute/`, data),
  writerResponse: (id, data) => apiClient.post(`/orders/disputes/${id}/writer-response/`, data),
}

