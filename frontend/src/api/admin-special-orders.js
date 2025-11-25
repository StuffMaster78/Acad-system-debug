import apiClient from './client'

export default {
  // Special Orders Management Dashboard
  getDashboard: () => apiClient.get('/admin-management/special-orders/dashboard/'),
  getApprovalQueue: (params) => apiClient.get('/admin-management/special-orders/approval-queue/', { params }),
  getEstimatedQueue: (params) => apiClient.get('/admin-management/special-orders/estimated-queue/', { params }),
  getInstallmentTracking: (params) => apiClient.get('/admin-management/special-orders/installment-tracking/', { params }),
  getAnalytics: (params) => apiClient.get('/admin-management/special-orders/analytics/', { params }),
  getConfigs: () => apiClient.get('/admin-management/special-orders/configs/'),
  createOrUpdateConfig: (data) => apiClient.post('/admin-management/special-orders/configs/', data),
}

