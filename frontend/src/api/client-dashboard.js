import apiClient from './client'

export default {
  // Get comprehensive client dashboard statistics
  getStats: (days = 30) => apiClient.get('/client-management/dashboard/stats/', { params: { days } }),
  
  // Get loyalty points summary and tier information
  getLoyalty: () => apiClient.get('/client-management/dashboard/loyalty/'),
  
  // Get order and spending analytics
  getAnalytics: (days = 30) => apiClient.get('/client-management/dashboard/analytics/', { params: { days } }),
  
  // Get wallet analytics and transaction history
  getWalletAnalytics: (days = 30) => apiClient.get('/client-management/dashboard/wallet/', { params: { days } }),
  
  // Get referral dashboard data
  getReferrals: () => apiClient.get('/client-management/dashboard/referrals/'),
  
  // Get order activity timeline
  getOrderActivityTimeline: (params) => apiClient.get('/client-management/dashboard/order-activity-timeline/', { params }),
}

