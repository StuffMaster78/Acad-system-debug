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
  
  // Geographic Analytics
  getGeographicAnalytics: (params) => apiClient.get('/admin-management/geographic-analytics/dashboard/', { params }),
  getAnalyticsByCountry: (params) => apiClient.get('/admin-management/geographic-analytics/by-country/', { params }),
  getAnalyticsByState: (params) => apiClient.get('/admin-management/geographic-analytics/by-state/', { params }),
  getAnalyticsBySubject: (params) => apiClient.get('/admin-management/geographic-analytics/by-subject/', { params }),
  
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
  
  // Performance Monitoring
  getPerformanceMetrics: () => apiClient.get('/admin-management/performance/metrics/'),
  getPerformanceStats: () => apiClient.get('/admin-management/performance/stats/'),
  getSlowEndpoints: (threshold = 500) => apiClient.get('/admin-management/performance/slow-endpoints/', { params: { threshold } }),
  getHighQueryEndpoints: (threshold = 10) => apiClient.get('/admin-management/performance/high-query-endpoints/', { params: { threshold } }),
  clearPerformanceMetrics: () => apiClient.post('/admin-management/performance/clear-metrics/'),
  
  // Email Digests
  listEmailDigests: (params) => apiClient.get('/admin-management/emails/digests/', { params }),
  getEmailDigest: (id) => apiClient.get(`/admin-management/emails/digests/${id}/`),
  createEmailDigest: (data) => apiClient.post('/admin-management/emails/digests/', data),
  updateEmailDigest: (id, data) => apiClient.patch(`/admin-management/emails/digests/${id}/`, data),
  deleteEmailDigest: (id) => apiClient.delete(`/admin-management/emails/digests/${id}/`),
  sendEmailDigest: (id) => apiClient.post(`/admin-management/emails/digests/${id}/send/`),
  sendDueDigests: () => apiClient.post('/admin-management/emails/digests/send_due/'),
  
  // Broadcast Messages
  listBroadcastMessages: (params) => apiClient.get('/admin-management/emails/broadcasts/', { params }),
  getBroadcastMessage: (id) => apiClient.get(`/admin-management/emails/broadcasts/${id}/`),
  createBroadcastMessage: (data) => apiClient.post('/admin-management/emails/broadcasts/', data),
  updateBroadcastMessage: (id, data) => apiClient.patch(`/admin-management/emails/broadcasts/${id}/`, data),
  deleteBroadcastMessage: (id) => apiClient.delete(`/admin-management/emails/broadcasts/${id}/`),
  sendBroadcastNow: (id) => apiClient.post(`/admin-management/emails/broadcasts/${id}/send_now/`),
  previewBroadcast: (id) => apiClient.post(`/admin-management/emails/broadcasts/${id}/preview/`),
  getBroadcastStats: (id) => apiClient.get(`/admin-management/emails/broadcasts/${id}/stats/`),
  
  // Rate Limiting Monitoring
  getRateLimitStats: (params) => apiClient.get('/admin-management/rate-limiting/stats/', { params }),
  getTopRateLimitedEndpoints: (limit = 10) => apiClient.get('/admin-management/rate-limiting/top-endpoints/', { params: { limit } }),
  getTopRateLimitedUsers: (limit = 10) => apiClient.get('/admin-management/rate-limiting/top-users/', { params: { limit } }),
  getTopRateLimitedIPs: (limit = 10) => apiClient.get('/admin-management/rate-limiting/top-ips/', { params: { limit } }),
  clearRateLimitStats: () => apiClient.post('/admin-management/rate-limiting/clear-stats/'),
  
  // Compression Monitoring
  getCompressionStats: (limit = 1000) => apiClient.get('/admin-management/compression/stats/', { params: { limit } }),
  clearCompressionStats: () => apiClient.post('/admin-management/compression/clear-stats/'),
  
  // System Health
  getSystemHealth: () => apiClient.get('/admin-management/system-health/health/'),
  getSystemAlerts: () => apiClient.get('/admin-management/system-health/alerts/'),
  
  // Financial Overview
  getFinancialOverview: (params) => apiClient.get('/admin-management/financial-overview/overview/', { params }),
  getAllPayments: (params) => apiClient.get('/admin-management/financial-overview/all-payments/', { params }),
  
  // Advanced Analytics Dashboard
  getAdvancedAnalytics: (params) => apiClient.get('/admin-management/advanced-analytics/', { params }),
  
  // Unified Search
  unifiedSearch: (query, types, limit = 10) => {
    const params = { q: query, limit }
    if (types && types.length > 0) params.types = types.join(',')
    return apiClient.get('/admin-management/unified-search/search/', { params })
  },
  
  // Exports
  exportOrders: (params) => apiClient.get('/admin-management/exports/orders/', { params, responseType: 'blob' }),
  exportPayments: (params) => apiClient.get('/admin-management/exports/payments/', { params, responseType: 'blob' }),
  exportUsers: (params) => apiClient.get('/admin-management/exports/users/', { params, responseType: 'blob' }),
  exportFinancial: (params) => apiClient.get('/admin-management/exports/financial/', { params, responseType: 'blob' }),
  
  // Duplicate Detection
  detectDuplicates: (params) => apiClient.get('/admin-management/duplicate-detection/detect/', { params }),
  getDuplicateStats: () => apiClient.get('/admin-management/duplicate-detection/stats/'),
  getUserDuplicates: (userId) => apiClient.get(`/admin-management/duplicate-detection/${userId}/user-duplicates/`),
  
  // Referral Tracking
  listReferrals: (params) => apiClient.get('/admin-management/referrals/tracking/', { params }),
  getReferralStats: () => apiClient.get('/admin-management/referrals/tracking/statistics/'),
  voidReferral: (id, reason) => apiClient.post(`/admin-management/referrals/tracking/${id}/void_referral/`, { reason }),
  
  // Referral Abuse
  listAbuseFlags: (params) => apiClient.get('/admin-management/referrals/abuse-flags/', { params }),
  createAbuseFlag: (data) => apiClient.post('/admin-management/referrals/abuse-flags/', data),
  resolveAbuseFlag: (id, data) => apiClient.patch(`/admin-management/referrals/abuse-flags/${id}/`, data),
  
  // Referral Codes
  listReferralCodes: (params) => apiClient.get('/admin-management/referrals/codes/', { params }),
  getReferralCode: (id) => apiClient.get(`/admin-management/referrals/codes/${id}/`),
  createReferralCode: (data) => apiClient.post('/admin-management/referrals/codes/', data),
  updateReferralCode: (id, data) => apiClient.patch(`/admin-management/referrals/codes/${id}/`, data),
  deleteReferralCode: (id) => apiClient.delete(`/admin-management/referrals/codes/${id}/`),
  traceReferralCode: (id) => apiClient.get(`/admin-management/referrals/codes/${id}/trace/`),
  generateReferralCodeForClient: (data) => apiClient.post('/admin-management/referrals/codes/generate-for-client/', data),
  getReferralCodeStatistics: () => apiClient.get('/admin-management/referrals/codes/statistics/'),
  
  // Loyalty Tracking
  listLoyaltyTransactions: (params) => apiClient.get('/admin-management/loyalty/tracking/', { params }),
  getLoyaltyStats: () => apiClient.get('/admin-management/loyalty/tracking/statistics/'),
  
  // Generic API methods for flexible endpoint access
  get: (path, config) => apiClient.get(`/admin-management${path}`, config),
  post: (path, data, config) => apiClient.post(`/admin-management${path}`, data, config),
  patch: (path, data, config) => apiClient.patch(`/admin-management${path}`, data, config),
  put: (path, data, config) => apiClient.put(`/admin-management${path}`, data, config),
  delete: (path, config) => apiClient.delete(`/admin-management${path}`, config),
}

