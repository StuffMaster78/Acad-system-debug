import apiClient from './client'

export default {
  // Writer Performance Snapshots
  listSnapshots: (params) => apiClient.get('/writer-management/writer-performance-snapshots/', { params }),
  getSnapshot: (id) => apiClient.get(`/writer-management/writer-performance-snapshots/${id}/`),
  
  // Writer Performance Dashboard (for individual writer)
  getDashboard: (writerId) => apiClient.get(`/writer-management/writer-performance-dashboard/${writerId}/`),
  
  // Writer Profiles (for getting writer list)
  listWriters: (params) => apiClient.get('/writer-management/writers/', { params }),
  getWriter: (id) => apiClient.get(`/writer-management/writers/${id}/`),
  
  // Badge Analytics
  getBadgeAnalytics: (params) => apiClient.get('/writer-management/badge-analytics/', { params }),
  getBadgeAchievements: (params) => apiClient.get('/writer-management/badge-achievements/', { params }),
  getWriterBadgePerformance: (writerId) => apiClient.get(`/writer-management/badge-performance/${writerId}/`),
}

