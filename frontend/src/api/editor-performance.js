import apiClient from './client'

export default {
  // Performance Metrics
  getPerformance: () => apiClient.get('/editor-management/performance/'),
  getDetailedStats: (params) => apiClient.get('/editor-management/performance/detailed_stats/', { params }),
  
  // Dashboard Stats (includes performance)
  getDashboardStats: (params) => apiClient.get('/editor-management/profiles/dashboard_stats/', { params }),
}

