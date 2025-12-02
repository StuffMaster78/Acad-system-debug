import apiClient from './client'

export default {
  // Refund Management Dashboard
  getDashboard: () => apiClient.get('/admin-management/refunds/dashboard/dashboard/'),
  getAnalytics: (params) => apiClient.get('/admin-management/refunds/dashboard/analytics/', { params }),
  getPendingRefunds: (params) => apiClient.get('/admin-management/refunds/dashboard/pending/', { params }),
  getHistory: (params) => apiClient.get('/admin-management/refunds/dashboard/history/', { params }),
  list: (params) => apiClient.get('/admin-management/refunds/', { params }),
  get: (id) => apiClient.get(`/admin-management/refunds/${id}/`),
  approve: (id, data) => apiClient.post(`/admin-management/refunds/${id}/approve/`, data),
  reject: (id, data) => apiClient.post(`/admin-management/refunds/${id}/reject/`, data),
  process: (id, data) => apiClient.post(`/admin-management/refunds/${id}/process/`, data),
}

