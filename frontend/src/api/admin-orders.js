import apiClient from './client'

export default {
  // Order Management Dashboard
  getDashboard: () => apiClient.get('/admin-management/orders/dashboard/'),
  getAnalytics: (params) => apiClient.get('/admin-management/orders/analytics/', { params }),
  getAssignmentQueue: (params) => apiClient.get('/admin-management/orders/assignment-queue/', { params }),
  getOverdueOrders: (params) => apiClient.get('/admin-management/orders/overdue/', { params }),
  getStuckOrders: (params) => apiClient.get('/admin-management/orders/stuck/', { params }),
  bulkAssign: (data) => apiClient.post('/admin-management/orders/bulk-assign/', data),
  bulkAction: (data) => apiClient.post('/admin-management/orders/bulk-action/', data),
  getOrderTimeline: (orderId) => apiClient.get(`/admin-management/orders/${orderId}/timeline/`),
}

