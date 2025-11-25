import apiClient from './client'

export default {
  // Get financial overview
  getOverview: (params) => apiClient.get('/admin-management/financial-overview/overview/', { params }),
  
  // Get all payments
  getAllPayments: (params) => apiClient.get('/admin-management/financial-overview/all-payments/', { params }),
}

