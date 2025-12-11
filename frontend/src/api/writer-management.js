import apiClient from './client'

export default {
  // Writer Level Configs (criteria-based levels)
  listWriterLevelConfigs: (params) => apiClient.get('/writer-management/writer-level-configs/', { params }),
  getWriterLevelConfig: (id) => apiClient.get(`/writer-management/writer-level-configs/${id}/`),
  createWriterLevelConfig: (data) => apiClient.post('/writer-management/writer-level-configs/', data),
  updateWriterLevelConfig: (id, data) => apiClient.patch(`/writer-management/writer-level-configs/${id}/`, data),
  deleteWriterLevelConfig: (id) => apiClient.delete(`/writer-management/writer-level-configs/${id}/`),
  // Writers
  listWriters: (params) => apiClient.get('/writer-management/writers/', { params }),
  getWriter: (id) => apiClient.get(`/writer-management/writers/${id}/`),
  
  // Writer Strikes
  listStrikes: (params) => apiClient.get('/writer-management/writer-strikes/', { params }),
  getStrike: (id) => apiClient.get(`/writer-management/writer-strikes/${id}/`),
  createStrike: (data) => apiClient.post('/writer-management/writer-strikes/', data),
  revokeStrike: (id) => apiClient.post(`/writer-management/writer-strikes/${id}/revoke/`),
  getStrikesByWriter: (writerId) => apiClient.get(`/writer-management/writer-strikes/by-writer/${writerId}/`),
  
  // Writer Discipline Config
  listDisciplineConfigs: (params) => apiClient.get('/writer-management/writer-discipline-configs/', { params }),
  getDisciplineConfig: (websiteId) => apiClient.get(`/writer-management/writer-discipline-configs/${websiteId}/`),
  getDisciplineConfigByWebsite: (websiteId) => apiClient.get(`/writer-management/writer-discipline-configs/by-website/${websiteId}/`),
  createDisciplineConfig: (data) => apiClient.post('/writer-management/writer-discipline-configs/', data),
  updateDisciplineConfig: (websiteId, data) => apiClient.patch(`/writer-management/writer-discipline-configs/${websiteId}/`, data),
  
  // Writer Warnings
  listWarnings: (params) => apiClient.get('/writer-management/writer-warnings/', { params }),
  getWarning: (id) => apiClient.get(`/writer-management/writer-warnings/${id}/`),
  createWarning: (data) => apiClient.post('/writer-management/writer-warnings/', data),
  deactivateWarning: (id) => apiClient.delete(`/writer-management/writer-warnings/${id}/`),
  
  // Writer Status
  getWriterStatus: (writerId) => apiClient.get(`/writer-management/writer-status/${writerId}/`),
  listWriterStatuses: (params) => apiClient.get('/writer-management/writer-status/', { params }),
  
  // Writer Profile
  getMyProfile: () => apiClient.get('/writer-management/writers/my_profile/'),
  
  // Writer Suspensions
  listSuspensions: (params) => apiClient.get('/writer-management/writer-suspensions/', { params }),
  getSuspension: (id) => apiClient.get(`/writer-management/writer-suspensions/${id}/`),
  
  // Writer Order Hold Requests
  listHoldRequests: (params) => apiClient.get('/writer-management/writer-order-hold-requests/', { params }),
  getHoldRequest: (id) => apiClient.get(`/writer-management/writer-order-hold-requests/${id}/`),
  createHoldRequest: (data) => apiClient.post('/writer-management/writer-order-hold-requests/', data),
  updateHoldRequest: (id, data) => apiClient.patch(`/writer-management/writer-order-hold-requests/${id}/`, data),
  
  // Deadline Extension Requests
  listDeadlineExtensionRequests: (params) => apiClient.get('/writer-management/writer-deadline-extension-requests/', { params }),
  getDeadlineExtensionRequest: (id) => apiClient.get(`/writer-management/writer-deadline-extension-requests/${id}/`),
  createDeadlineExtensionRequest: (data) => apiClient.post('/writer-management/writer-deadline-extension-requests/', data),
  updateDeadlineExtensionRequest: (id, data) => apiClient.patch(`/writer-management/writer-deadline-extension-requests/${id}/`, data),
  
  // Badge Analytics
  getBadgeAnalytics: (params) => apiClient.get('/writer-management/badge-analytics/', { params }),
  getBadgeDistribution: () => apiClient.get('/writer-management/badge-analytics/distribution/'),
  getBadgeTrends: (days = 30) => apiClient.get('/writer-management/badge-analytics/trends/', { params: { days } }),
  getBadgeLeaderboard: (type = null, limit = 10) => apiClient.get('/writer-management/badge-analytics/leaderboard/', { params: { type, limit } }),
  getBadgeAchievements: (params) => apiClient.get('/writer-management/badge-achievements/', { params }),
  getBadgePerformance: (params) => apiClient.get('/writer-management/badge-performance/', { params }),
  
  // Writer Portfolios
  listPortfolios: (params) => apiClient.get('/writer-management/writer-portfolios/', { params }),
  getPortfolio: (id) => apiClient.get(`/writer-management/writer-portfolios/${id}/`),
  createPortfolio: (data) => apiClient.post('/writer-management/writer-portfolios/', data),
  updatePortfolio: (id, data) => apiClient.patch(`/writer-management/writer-portfolios/${id}/`, data),
  deletePortfolio: (id) => apiClient.delete(`/writer-management/writer-portfolios/${id}/`),
  
  // Portfolio Samples
  listPortfolioSamples: (params) => apiClient.get('/writer-management/portfolio-samples/', { params }),
  getPortfolioSample: (id) => apiClient.get(`/writer-management/portfolio-samples/${id}/`),
  createPortfolioSample: (data) => apiClient.post('/writer-management/portfolio-samples/', data),
  updatePortfolioSample: (id, data) => apiClient.patch(`/writer-management/portfolio-samples/${id}/`, data),
  deletePortfolioSample: (id) => apiClient.delete(`/writer-management/portfolio-samples/${id}/`),
  
  // Feedback
  listFeedback: (params) => apiClient.get('/writer-management/feedback/', { params }),
  getFeedback: (id) => apiClient.get(`/writer-management/feedback/${id}/`),
  createFeedback: (data) => apiClient.post('/writer-management/feedback/', data),
  updateFeedback: (id, data) => apiClient.patch(`/writer-management/feedback/${id}/`, data),
  deleteFeedback: (id) => apiClient.delete(`/writer-management/feedback/${id}/`),
  
  // Feedback History
  listFeedbackHistory: (params) => apiClient.get('/writer-management/feedback-history/', { params }),
  getFeedbackHistory: (id) => apiClient.get(`/writer-management/feedback-history/${id}/`),
  
  // Performance Snapshots
  listPerformanceSnapshots: (params) => apiClient.get('/writer-management/writer-performance-snapshots/', { params }),
  getPerformanceSnapshot: (id) => apiClient.get(`/writer-management/writer-performance-snapshots/${id}/`),
  
  // Writer Payments
  listPayments: (params) => apiClient.get('/writer-management/writer-payments/', { params }),
  getPayment: (id) => apiClient.get(`/writer-management/writer-payments/${id}/`),
  downloadReceipt: (id) => apiClient.get(`/writer-management/writer-payments/${id}/receipt/`, { responseType: 'blob' }),
}

