import apiClient from './client'

export default {
  getSummary: () => apiClient.get('/loyalty_management/loyalty/summary/'),
  convertPoints: (points) => apiClient.post('/loyalty_management/loyalty/convert/', { points }),
  getTransactions: (params) => apiClient.get('/loyalty_management/loyalty/transactions/', { params }),
  // Redemption
  getRedemptionItems: (params) => apiClient.get('/loyalty_management/redemption-items/', { params }),
  getRedemptionItem: (id) => apiClient.get(`/loyalty_management/redemption-items/${id}/`),
  getRedemptionRequests: (params) => apiClient.get('/loyalty_management/redemption-requests/', { params }),
  createRedemptionRequest: (data) => apiClient.post('/loyalty_management/redemption-requests/', data),
  cancelRedemptionRequest: (id) => apiClient.post(`/loyalty_management/redemption-requests/${id}/cancel/`),
  getRedemptionCategories: (params) => apiClient.get('/loyalty_management/redemption-categories/', { params }),
}

