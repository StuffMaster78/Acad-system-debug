import apiClient from './client'

export default {
  // Refund Management Dashboard
  getDashboard: () => apiClient.get('/admin-management/refunds/dashboard/'),
  getAnalytics: (params) => apiClient.get('/admin-management/refunds/analytics/', { params }),
  getPendingRefunds: (params) => apiClient.get('/admin-management/refunds/pending/', { params }),
  getHistory: (params) => apiClient.get('/admin-management/refunds/history/', { params }),
}

