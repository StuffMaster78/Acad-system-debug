import apiClient from './client'

export default {
  getDashboard: () => apiClient.get('/support-management/dashboard/'),
  getNotifications: (params) => apiClient.get('/support-management/notifications/', { params }),
  getOrderManagement: (params) => apiClient.get('/support-management/order-management/', { params }),
  getTickets: (params) => apiClient.get('/tickets/tickets/', { params }),
}

