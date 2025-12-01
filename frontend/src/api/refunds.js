import apiClient from './client'

export default {
  // Refunds
  list: (params) => apiClient.get('/refunds/refunds/', { params }),
  get: (id) => apiClient.get(`/refunds/refunds/${id}/`),
  create: (data) => apiClient.post('/refunds/refunds/', data),
  process: (id, data) => apiClient.post(`/refunds/refunds/${id}/process/`, data),
  retry: (id) => apiClient.post(`/refunds/refunds/${id}/retry/`),
  cancel: (id, data) => apiClient.post(`/refunds/refunds/${id}/cancel/`, data),
  
  // Refund Logs
  listLogs: (params) => apiClient.get('/refunds/refund-logs/', { params }),
  getLog: (id) => apiClient.get(`/refunds/refund-logs/${id}/`),
  
  // Refund Receipts
  listReceipts: (params) => apiClient.get('/refunds/refund-receipts/', { params }),
  getReceipt: (id) => apiClient.get(`/refunds/refund-receipts/${id}/`),
}

