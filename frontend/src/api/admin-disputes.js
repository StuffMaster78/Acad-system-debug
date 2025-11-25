import apiClient from './client'

export default {
  // Dispute Management Dashboard
  getDashboard: () => apiClient.get('/admin-management/disputes/dashboard/'),
  getAnalytics: (params) => apiClient.get('/admin-management/disputes/analytics/', { params }),
  getPendingDisputes: (params) => apiClient.get('/admin-management/disputes/pending/', { params }),
  bulkResolve: (data) => apiClient.post('/admin-management/disputes/bulk-resolve/', data),
}

