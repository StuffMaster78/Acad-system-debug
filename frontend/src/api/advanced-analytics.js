import apiClient from './client'

const advancedAnalyticsAPI = {
  // Summary Metrics
  getSummary() {
    return apiClient.get('/admin-management/dashboard/metrics/summary/')
  },
  
  // Revenue Analytics
  getYearlyOrders(year = null) {
    const params = year ? { year } : {}
    return apiClient.get('/admin-management/dashboard/metrics/yearly-orders/', { params })
  },
  
  getYearlyEarnings(year = null) {
    const params = year ? { year } : {}
    return apiClient.get('/admin-management/dashboard/metrics/yearly-earnings/', { params })
  },
  
  getMonthlyOrders(year = null, month = null) {
    const params = {}
    if (year) params.year = year
    if (month) params.month = month
    return apiClient.get('/admin-management/dashboard/metrics/monthly-orders/', { params })
  },
  
  getServiceRevenue(days = 30) {
    return apiClient.get('/admin-management/dashboard/metrics/service-revenue/', { params: { days } })
  },
  
  getPaymentStatus() {
    return apiClient.get('/admin-management/dashboard/metrics/payment-status/')
  },
  
  // User Growth (using existing user management endpoints)
  getUserStats() {
    return apiClient.get('/admin-management/user-management/stats/')
  },
  
  // Additional metrics from dashboard
  getDashboardStats() {
    return apiClient.get('/admin-management/dashboard/')
  },
}

export default advancedAnalyticsAPI

