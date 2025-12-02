import apiClient from './client'

export default {
  // Dispute Management Dashboard
  getDashboard: () => apiClient.get('/admin-management/disputes/dashboard/dashboard/'),
  getAnalytics: (params) => apiClient.get('/admin-management/disputes/dashboard/analytics/', { params }),
  getPendingDisputes: (params) => apiClient.get('/admin-management/disputes/dashboard/pending/', { params }),
  list: (params) => apiClient.get('/admin-management/disputes/', { params }),
  get: (id) => apiClient.get(`/admin-management/disputes/${id}/`),
  resolve: (id, data) => apiClient.post(`/admin-management/disputes/${id}/resolve/`, data),
  bulkResolve: (data) => apiClient.post('/admin-management/disputes/bulk-resolve/', data),
}

