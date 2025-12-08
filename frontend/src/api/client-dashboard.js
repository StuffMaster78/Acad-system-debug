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
  
  // Get enhanced order status (detailed status with progress tracking)
  getEnhancedOrderStatus: (orderId) => apiClient.get('/client-management/dashboard/enhanced-order-status/', { params: { order_id: orderId } }),
  
  // Payment reminders
  getPaymentReminders: () => apiClient.get('/client-management/dashboard/payment-reminders/'),
  createPaymentReminder: (data) => apiClient.post('/client-management/dashboard/payment-reminders/create/', data),
  updatePaymentReminder: (reminderId, data) => apiClient.patch(`/client-management/dashboard/payment-reminders/${reminderId}/update/`, data),
}

