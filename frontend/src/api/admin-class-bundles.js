import apiClient from './client'

export default {
  // Class Bundles Management Dashboard
  getDashboard: () => apiClient.get('/admin-management/class-bundles/dashboard/'),
  getInstallmentTracking: (params) => apiClient.get('/admin-management/class-bundles/installment-tracking/', { params }),
  getDepositPending: (params) => apiClient.get('/admin-management/class-bundles/deposit-pending/', { params }),
  getAnalytics: (params) => apiClient.get('/admin-management/class-bundles/analytics/', { params }),
  getConfigs: () => apiClient.get('/admin-management/class-bundles/configs/'),
  createOrUpdateConfig: (data) => apiClient.post('/admin-management/class-bundles/configs/', data),
  getCommunicationThreads: (params) => apiClient.get('/admin-management/class-bundles/communication-threads/', { params }),
  getSupportTickets: (params) => apiClient.get('/admin-management/class-bundles/support-tickets/', { params }),
}

