import apiClient from './client'

const loyaltyAPI = {
  // Conversion Configuration
  getConversionConfig() {
    // Try the ViewSet endpoint first, fallback to admin endpoint
    return apiClient.get('/loyalty-management/loyalty-points-conversion-config/').catch(() => {
      return apiClient.get('/loyalty-management/admin/loyalty-conversion-config/')
    })
  },
  
  updateConversionConfig(data) {
    return apiClient.post('/loyalty-management/admin/loyalty-conversion-config/', data)
  },

  // Tiers Management
  listTiers() {
    return apiClient.get('/loyalty-management/loyalty-tiers/')
  },
  
  getTier(id) {
    return apiClient.get(`/loyalty-management/loyalty-tiers/${id}/`)
  },
  
  createTier(data) {
    return apiClient.post('/loyalty-management/loyalty-tiers/', data)
  },
  
  updateTier(id, data) {
    return apiClient.put(`/loyalty-management/loyalty-tiers/${id}/`, data)
  },
  
  deleteTier(id) {
    return apiClient.delete(`/loyalty-management/loyalty-tiers/${id}/`)
  },

  // Transactions
  listTransactions(params = {}) {
    return apiClient.get('/loyalty-management/loyalty-transactions/', { params })
  },
  
  getTransaction(id) {
    return apiClient.get(`/loyalty-management/loyalty-transactions/${id}/`)
  },

  // Point Management
  awardPoints(data) {
    return apiClient.post('/loyalty-management/admin/award-loyalty/', data)
  },
  
  deductPoints(data) {
    return apiClient.post('/loyalty-management/admin/deduct-loyalty/', data)
  },
  
  transferPoints(data) {
    return apiClient.post('/loyalty-management/admin/transfer-loyalty/', data)
  },
  
  forceConvert(data) {
    return apiClient.post(`/loyalty-management/admin/force-convert/${data.client_id}/`, data)
  },

  // Milestones
  listMilestones() {
    return apiClient.get('/loyalty-management/milestones/')
  },
  
  getMilestone(id) {
    return apiClient.get(`/loyalty-management/milestones/${id}/`)
  },
  
  createMilestone(data) {
    return apiClient.post('/loyalty-management/milestones/', data)
  },
  
  updateMilestone(id, data) {
    return apiClient.put(`/loyalty-management/milestones/${id}/`, data)
  },
  
  deleteMilestone(id) {
    return apiClient.delete(`/loyalty-management/milestones/${id}/`)
  },

  // Badges
  listBadges(params = {}) {
    return apiClient.get('/loyalty-management/client-badges/', { params })
  },
  
  getBadge(id) {
    return apiClient.get(`/loyalty-management/client-badges/${id}/`)
  },

  // Redemption Categories
  listRedemptionCategories() {
    return apiClient.get('/loyalty-management/redemption-categories/')
  },
  
  createRedemptionCategory(data) {
    return apiClient.post('/loyalty-management/redemption-categories/', data)
  },
  
  updateRedemptionCategory(id, data) {
    return apiClient.put(`/loyalty-management/redemption-categories/${id}/`, data)
  },
  
  deleteRedemptionCategory(id) {
    return apiClient.delete(`/loyalty-management/redemption-categories/${id}/`)
  },

  // Redemption Items
  listRedemptionItems(params = {}) {
    return apiClient.get('/loyalty-management/redemption-items/', { params })
  },
  
  getRedemptionItems(params = {}) {
    return apiClient.get('/loyalty-management/redemption-items/', { params })
  },
  
  getRedemptionItem(id) {
    return apiClient.get(`/loyalty-management/redemption-items/${id}/`)
  },
  
  createRedemptionItem(data) {
    return apiClient.post('/loyalty-management/redemption-items/', data)
  },
  
  updateRedemptionItem(id, data) {
    return apiClient.put(`/loyalty-management/redemption-items/${id}/`, data)
  },
  
  deleteRedemptionItem(id) {
    return apiClient.delete(`/loyalty-management/redemption-items/${id}/`)
  },

  // Redemption Requests
  listRedemptionRequests(params = {}) {
    return apiClient.get('/loyalty-management/redemption-requests/', { params })
  },
  
  getRedemptionRequest(id) {
    return apiClient.get(`/loyalty-management/redemption-requests/${id}/`)
  },
  
  createRedemptionRequest(data) {
    return apiClient.post('/loyalty-management/redemption-requests/', data)
  },
  
  approveRedemption(id, data = {}) {
    return apiClient.post(`/loyalty-management/redemption-requests/${id}/approve/`, data)
  },
  
  rejectRedemption(id, data = {}) {
    return apiClient.post(`/loyalty-management/redemption-requests/${id}/reject/`, data)
  },

  // Analytics
  listAnalytics(params = {}) {
    return apiClient.get('/loyalty-management/analytics/', { params })
  },
  
  getAnalytics(id) {
    return apiClient.get(`/loyalty-management/analytics/${id}/`)
  },
  
  calculateAnalytics(data) {
    return apiClient.post('/loyalty-management/analytics/calculate/', data)
  },
  
  getPointsTrend(days = 30) {
    return apiClient.get('/loyalty-management/analytics/points_trend/', { params: { days } })
  },
  
  getTopRedemptions(limit = 10) {
    return apiClient.get('/loyalty-management/analytics/top_redemptions/', { params: { limit } })
  },
  
  getTierDistribution() {
    return apiClient.get('/loyalty-management/analytics/tier_distribution/')
  },
  
  getEngagementStats(days = 30) {
    return apiClient.get('/loyalty-management/analytics/engagement_stats/', { params: { days } })
  },

  // Dashboard Widgets
  listWidgets() {
    return apiClient.get('/loyalty-management/dashboard-widgets/')
  },
  
  createWidget(data) {
    return apiClient.post('/loyalty-management/dashboard-widgets/', data)
  },
  
  updateWidget(id, data) {
    return apiClient.put(`/loyalty-management/dashboard-widgets/${id}/`, data)
  },
  
  deleteWidget(id) {
    return apiClient.delete(`/loyalty-management/dashboard-widgets/${id}/`)
  },
}

export default loyaltyAPI

