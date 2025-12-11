import apiClient from './client'

export default {
  // Superadmin Logs
  listLogs: (params) => apiClient.get('/superadmin-management/logs/', { params }),
  getLog: (id) => apiClient.get(`/superadmin-management/logs/${id}/`),
  
  // Superadmin Profile
  getProfile: () => apiClient.get('/superadmin-management/superadmin-profile/'),
  updateProfile: (data) => apiClient.patch('/superadmin-management/superadmin-profile/', data),
  
  // Superadmin Dashboard
  getDashboardStats: () => apiClient.get('/superadmin-management/dashboard/'),
  
  // User Management
  listUsers: (params) => apiClient.get('/superadmin-management/users/', { params }),
  getUser: (id) => apiClient.get(`/superadmin-management/users/${id}/`),
  changeUserRole: (userId, role) => apiClient.post('/superadmin-management/users/change_user_role/', { user_id: userId, role }),
  
  // Appeals
  listAppeals: (params) => apiClient.get('/superadmin-management/appeals/', { params }),
  getAppeal: (id) => apiClient.get(`/superadmin-management/appeals/${id}/`),
  updateAppeal: (id, data) => apiClient.patch(`/superadmin-management/appeals/${id}/`, data),
  
  // Tenant Management
  listTenants: (params) => apiClient.get('/superadmin-management/tenants/', { params }),
  getTenant: (id) => apiClient.get(`/superadmin-management/tenants/${id}/`),
  createTenant: (data) => apiClient.post('/superadmin-management/tenants/', data),
  updateTenant: (id, data) => apiClient.patch(`/superadmin-management/tenants/${id}/`, data),
  deleteTenant: (id) => apiClient.delete(`/superadmin-management/tenants/${id}/`),
}

