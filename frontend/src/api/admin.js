import apiClient from './client'

export default {
  // Admin order placement
  placeOrder: (data) => apiClient.post('/admin-management/place-order/', data),
  
  // Admin dashboard
  getDashboard: () => apiClient.get('/admin-management/dashboard/'),
  getOrderMetrics: () => apiClient.get('/admin-management/metrics/order-status/'),
  getPaymentMetrics: () => apiClient.get('/admin-management/metrics/payment-status/'),
  
  // User management
  listUsers: (params) => apiClient.get('/users/users/', { params }),
  getUser: (id) => apiClient.get(`/users/users/${id}/`),
  updateUser: (id, data) => apiClient.patch(`/users/users/${id}/`, data),
  
  // Order management
  getOrderDashboard: () => apiClient.get('/admin-management/orders/dashboard/'),
  getOrderAnalytics: (params) => apiClient.get('/admin-management/orders/analytics/', { params }),
  getAssignmentQueue: (params) => apiClient.get('/admin-management/orders/assignment-queue/', { params }),
  getOverdueOrders: (params) => apiClient.get('/admin-management/orders/overdue/', { params }),
  getStuckOrders: (params) => apiClient.get('/admin-management/orders/stuck/', { params }),
  bulkAssign: (data) => apiClient.post('/admin-management/orders/bulk-assign/', data),
  bulkAction: (data) => apiClient.post('/admin-management/orders/bulk-action/', data),
  getOrderTimeline: (orderId) => apiClient.get(`/admin-management/orders/${orderId}/timeline/`),
}

