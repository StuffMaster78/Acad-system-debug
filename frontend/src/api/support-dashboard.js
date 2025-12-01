import apiClient from './client'

export default {
  getDashboard: () => apiClient.get('/support-management/dashboard/'),
  getNotifications: (params) => apiClient.get('/support-management/notifications/', { params }),
  getOrderManagement: (params) => apiClient.get('/support-management/order-management/', { params }),
  getTickets: (params) => apiClient.get('/tickets/tickets/', { params }),
  getDashboardTickets: (params) => apiClient.get('/support-management/dashboard/tickets/', { params }),
  getDashboardOrders: (params) => apiClient.get('/support-management/dashboard/orders/', { params }),
  getDashboardEscalations: (params) => apiClient.get('/support-management/dashboard/escalations/', { params }),
  getAnalyticsPerformance: (params) => apiClient.get('/support-management/dashboard/analytics/performance/', { params }),
  getAnalyticsTrends: (params) => apiClient.get('/support-management/dashboard/analytics/trends/', { params }),
  getAnalyticsComparison: (params) => apiClient.get('/support-management/dashboard/analytics/comparison/', { params }),
}

