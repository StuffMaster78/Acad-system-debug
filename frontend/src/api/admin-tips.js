import apiClient from './client'

export default {
  // Tip Management Dashboard
  getDashboard: (params) => apiClient.get('/admin-management/tips/dashboard/', { params }),
  listTips: (params) => apiClient.get('/admin-management/tips/list_tips/', { params }),
  getAnalytics: (params) => apiClient.get('/admin-management/tips/analytics/', { params }),
  getEarnings: (params) => apiClient.get('/admin-management/tips/earnings/', { params }),
}

