import apiClient from './client'

export default {
  // Full dashboard data (includes all stats, user counts, recent logs)
  getDashboard: (params = {}) => apiClient.get('/admin-management/dashboard/', { params }),
  
  // Summary metrics (orders, revenue, tickets)
  getSummary: () => apiClient.get('/admin-management/dashboard/metrics/summary/'),
  
  // Yearly metrics
  getYearlyOrders: (year) => apiClient.get('/admin-management/dashboard/metrics/yearly-orders/', { params: { year } }),
  getYearlyEarnings: (year) => apiClient.get('/admin-management/dashboard/metrics/yearly-earnings/', { params: { year } }),
  
  // Monthly metrics
  getMonthlyOrders: (year, month) => apiClient.get('/admin-management/dashboard/metrics/monthly-orders/', { params: { year, month } }),
  
  // Service revenue
  getServiceRevenue: (days = 30) => apiClient.get('/admin-management/dashboard/metrics/service-revenue/', { params: { days } }),
  
  // Payment status
  getPaymentStatus: () => apiClient.get('/admin-management/dashboard/metrics/payment-status/'),
  
  // Place order (admin only)
  placeOrder: (data) => apiClient.post('/admin-management/dashboard/place-order/', data),
  
  // Activity logs
  getActivityLogs: (params) => apiClient.get('/admin-management/activity-logs/', { params }),
  
  // Legacy endpoints (for backward compatibility)
  getStats: () => apiClient.get('/admin-management/dashboard/'),
  getRecentActivity: () => apiClient.get('/admin-management/dashboard/'),
}

