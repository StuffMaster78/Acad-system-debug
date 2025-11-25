import apiClient from './client'

export default {
  // Detect duplicate accounts
  detectDuplicates: (params) => apiClient.get('/admin-management/duplicate-detection/detect/', { params }),
  
  // Get duplicates by role
  getDuplicatesByRole: (role, params) => apiClient.get(`/admin-management/duplicate-detection/by-role/${role}/`, { params }),
  
  // Get duplicates for a specific user
  getUserDuplicates: (userId) => apiClient.get(`/admin-management/duplicate-detection/${userId}/user-duplicates/`),
  
  // Get statistics
  getStats: () => apiClient.get('/admin-management/duplicate-detection/stats/'),
}

