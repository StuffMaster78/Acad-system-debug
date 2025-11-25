import apiClient from './client'

export default {
  // Loyalty Points Tracking
  listTransactions: (params) => apiClient.get('/admin-management/loyalty/tracking/', { params }),
  getTransaction: (id) => apiClient.get(`/admin-management/loyalty/tracking/${id}/`),
  getStatistics: () => apiClient.get('/admin-management/loyalty/tracking/statistics/'),
  getAwardSources: () => apiClient.get('/admin-management/loyalty/tracking/award-sources/'),
  getClientSummary: (clientId) => apiClient.get('/admin-management/loyalty/tracking/client-summary/', { params: { client_id: clientId } }),
}

