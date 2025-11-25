import apiClient from './client'

const pricingAnalyticsAPI = {
  // Overview
  getOverview(days = 30) {
    return apiClient.get('/pricing-configs/analytics/overview/', { params: { days } })
  },
  
  // Trends
  getTrends(days = 30) {
    return apiClient.get('/pricing-configs/analytics/trends/', { params: { days } })
  },
  
  // Service Breakdown
  getServiceBreakdown(days = 30) {
    return apiClient.get('/pricing-configs/analytics/service-breakdown/', { params: { days } })
  },
  
  // Academic Level Breakdown
  getAcademicLevelBreakdown(days = 30) {
    return apiClient.get('/pricing-configs/analytics/academic-level-breakdown/', { params: { days } })
  },
  
  // Pricing Configs
  getPricingConfigs() {
    return apiClient.get('/pricing-configs/analytics/pricing-configs/')
  },
  
  // Additional Services
  getAdditionalServices(days = 30) {
    return apiClient.get('/pricing-configs/analytics/additional-services/', { params: { days } })
  },
}

export default pricingAnalyticsAPI

