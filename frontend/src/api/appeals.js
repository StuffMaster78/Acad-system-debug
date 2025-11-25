import apiClient from './client'

export default {
  // Appeals
  listAppeals: (params) => apiClient.get('/superadmin-management/appeals/', { params }),
  getAppeal: (id) => apiClient.get(`/superadmin-management/appeals/${id}/`),
  createAppeal: (data) => apiClient.post('/superadmin-management/appeals/', data),
  updateAppeal: (id, data) => apiClient.patch(`/superadmin-management/appeals/${id}/`, data),
  approveAppeal: (id) => apiClient.post(`/superadmin-management/appeals/${id}/approve/`),
  rejectAppeal: (id) => apiClient.post(`/superadmin-management/appeals/${id}/reject/`),
  getPendingAppeals: () => apiClient.get('/superadmin-management/appeals/pending/'),
}

