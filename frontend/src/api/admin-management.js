import apiClient from './client'

export default {
  // User Management
  listUsers: (params) => apiClient.get('/admin-management/user-management/', { params }),
  getUser: (id) => apiClient.get(`/admin-management/user-management/${id}/`),
  createUser: (data) => apiClient.post('/admin-management/user-management/', data),
  updateUser: (id, data) => apiClient.put(`/admin-management/user-management/${id}/`, data),
  patchUser: (id, data) => apiClient.patch(`/admin-management/user-management/${id}/`, data),
  deleteUser: (id) => apiClient.delete(`/admin-management/user-management/${id}/`),
  
  // User Actions
  suspendUser: (id, reason, durationDays) => apiClient.post(`/admin-management/user-management/${id}/suspend/`, { reason, duration_days: durationDays }),
  unsuspendUser: (id) => apiClient.post(`/admin-management/user-management/${id}/unsuspend/`),
  blacklistUser: (id, reason) => apiClient.post(`/admin-management/user-management/${id}/blacklist/`, { reason }),
  placeOnProbation: (id, reason, durationDays) => apiClient.post(`/admin-management/user-management/${id}/place_on_probation/`, { reason, duration_days: durationDays }),
  removeFromProbation: (id) => apiClient.post(`/admin-management/user-management/${id}/remove_from_probation/`),
  changeRole: (id, role) => apiClient.post(`/admin-management/user-management/${id}/change_role/`, { role }),
  promoteToAdmin: (id) => apiClient.post(`/admin-management/user-management/${id}/promote_to_admin/`),
  resetPassword: (id) => apiClient.post(`/admin-management/user-management/${id}/reset_password/`),
  getUserStats: () => apiClient.get('/admin-management/user-management/stats/'),
  bulkActivate: (userIds) => apiClient.post('/admin-management/user-management/bulk_activate/', { user_ids: userIds }),
  bulkSuspend: (userIds, reason, durationDays) => apiClient.post('/admin-management/user-management/bulk_suspend/', { user_ids: userIds, reason, duration_days: durationDays }),
  
  // Configuration Management
  listPricingConfigs: (params) => apiClient.get('/admin-management/configs/pricing/', { params }),
  getPricingConfig: (id) => apiClient.get(`/admin-management/configs/pricing/${id}/`),
  createPricingConfig: (data) => apiClient.post('/admin-management/configs/pricing/', data),
  updatePricingConfig: (id, data) => apiClient.put(`/admin-management/configs/pricing/${id}/`, data),
  deletePricingConfig: (id) => apiClient.delete(`/admin-management/configs/pricing/${id}/`),
  
  listWriterConfigs: (params) => apiClient.get('/admin-management/configs/writer/', { params }),
  getWriterConfig: (id) => apiClient.get(`/admin-management/configs/writer/${id}/`),
  createWriterConfig: (data) => apiClient.post('/admin-management/configs/writer/', data),
  updateWriterConfig: (id, data) => apiClient.put(`/admin-management/configs/writer/${id}/`, data),
  
  listDiscountConfigs: (params) => apiClient.get('/admin-management/configs/discount/', { params }),
  getDiscountConfig: (id) => apiClient.get(`/admin-management/configs/discount/${id}/`),
  createDiscountConfig: (data) => apiClient.post('/admin-management/configs/discount/', data),
  updateDiscountConfig: (id, data) => apiClient.put(`/admin-management/configs/discount/${id}/`, data),
  
  listNotificationConfigs: (params) => apiClient.get('/admin-management/configs/notifications/', { params }),
  getNotificationConfig: (id) => apiClient.get(`/admin-management/configs/notifications/${id}/`),
  createNotificationConfig: (data) => apiClient.post('/admin-management/configs/notifications/', data),
  updateNotificationConfig: (id, data) => apiClient.put(`/admin-management/configs/notifications/${id}/`, data),
  
  listAllConfigs: () => apiClient.get('/admin-management/configs/list_all_configs/'),
  
  // System Health
  getSystemHealth: () => apiClient.get('/admin-management/system-health/health/'),
  getSystemAlerts: () => apiClient.get('/admin-management/system-health/alerts/'),
  
  // Enhanced Analytics
  getEnhancedAnalytics: (days = 30) => apiClient.get('/admin-management/dashboard/analytics/enhanced/', { params: { days } }),
  getComparativeAnalytics: (period1Days = 30, period2Days = 30) => apiClient.get('/admin-management/dashboard/analytics/compare/', { params: { period1_days: period1Days, period2_days: period2Days } }),
  
  // Fines Management Dashboard
  getFinesDashboard: () => apiClient.get('/admin-management/fines/dashboard/'),
  getFinesDashboardAnalytics: (params) => apiClient.get('/admin-management/fines/dashboard/analytics/', { params }),
  getFinesDisputeQueue: (params) => apiClient.get('/admin-management/fines/dashboard/dispute-queue/', { params }),
  getFinesActiveFines: (params) => apiClient.get('/admin-management/fines/dashboard/active-fines/', { params }),
  getPendingFines: (params) => apiClient.get('/admin-management/fines/pending/', { params }),
  getAppealsQueue: (params) => apiClient.get('/admin-management/fines/appeals/', { params }),
      getFinesAnalytics: (params) => apiClient.get('/admin-management/fines/analytics/', { params }),
      waiveFine: (id, data) => apiClient.post(`/admin-management/fines/${id}/waive/`, data),
      
      // Advanced Analytics
      getAdvancedAnalytics: (params) => apiClient.get('/admin-management/advanced-analytics/dashboard/', { params }),
      getAdvancedAnalyticsComparison: (params) => apiClient.get('/admin-management/advanced-analytics/comparison/', { params }),
  voidFine: (id, data) => apiClient.post(`/admin-management/fines/${id}/void/`, data),
  approveAppeal: (id, data) => apiClient.post(`/admin-management/fines/${id}/appeals/approve/`, data),
  rejectAppeal: (id, data) => apiClient.post(`/admin-management/fines/${id}/appeals/reject/`, data),
}

