import apiClient from './client'

export default {
  getDashboard: () => apiClient.get('/superadmin-management/dashboard/'),
  getUsers: (params) => apiClient.get('/superadmin-management/users/', { params }),
  getLogs: (params) => apiClient.get('/superadmin-management/logs/', { params }),
}

