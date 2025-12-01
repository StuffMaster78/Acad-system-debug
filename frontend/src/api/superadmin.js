import apiClient from './client'

const superadminAPI = {
  // Dashboard
  getDashboard() {
    // ViewSet list action
    return apiClient.get('/superadmin-management/dashboard/').catch(() => {
      // Fallback: use admin dashboard if superadmin dashboard fails
      return apiClient.get('/admin-management/dashboard/')
    })
  },
  
  // User Management
  listUsers(params = {}) {
    return apiClient.get('/superadmin-management/users/', { params })
  },
  
  getUser(id) {
    return apiClient.get(`/superadmin-management/users/${id}/`)
  },
  
  createUser(data) {
    return apiClient.post('/superadmin-management/users/create_user/', data)
  },
  
  suspendUser(data) {
    return apiClient.post('/superadmin-management/users/suspend_user/', data)
  },
  
  reactivateUser(data) {
    return apiClient.post('/superadmin-management/users/reactivate_user/', data)
  },
  
  changeUserRole(data) {
    return apiClient.post('/superadmin-management/users/change_user_role/', data)
  },
  
  // Superadmin Profiles
  listProfiles(params = {}) {
    return apiClient.get('/superadmin-management/superadmin-profile/', { params })
  },
  
  getProfile(id) {
    return apiClient.get(`/superadmin-management/superadmin-profile/${id}/`)
  },
  
  createProfile(data) {
    return apiClient.post('/superadmin-management/superadmin-profile/', data)
  },
  
  updateProfile(id, data) {
    return apiClient.put(`/superadmin-management/superadmin-profile/${id}/`, data)
  },
  
  deleteProfile(id) {
    return apiClient.delete(`/superadmin-management/superadmin-profile/${id}/`)
  },
  
  // Logs
  listLogs(params = {}) {
    return apiClient.get('/superadmin-management/logs/', { params })
  },
  
  getLog(id) {
    return apiClient.get(`/superadmin-management/logs/${id}/`)
  },
  
  // Websites/Tenants (using websites API - legacy)
  listWebsites(params = {}) {
    return apiClient.get('/websites/websites/', { params })
  },
  
  getWebsite(id) {
    return apiClient.get(`/websites/websites/${id}/`)
  },
  
  createWebsite(data) {
    return apiClient.post('/websites/websites/', data)
  },
  
  updateWebsite(id, data) {
    return apiClient.put(`/websites/websites/${id}/`, data)
  },
  
  deleteWebsite(id) {
    return apiClient.delete(`/websites/websites/${id}/`)
  },
  
  // Tenant Management (new comprehensive endpoints)
  listTenants(params = {}) {
    return apiClient.get('/superadmin-management/tenants/list_tenants/', { params })
  },
  
  createTenant(data) {
    return apiClient.post('/superadmin-management/tenants/create_tenant/', data)
  },
  
  getTenantDetails(id) {
    return apiClient.get(`/superadmin-management/tenants/${id}/tenant_details/`)
  },
  
  updateTenant(id, data) {
    return apiClient.patch(`/superadmin-management/tenants/${id}/update_tenant/`, data)
  },
  
  deleteTenant(id) {
    return apiClient.delete(`/superadmin-management/tenants/${id}/delete_tenant/`)
  },
  
  restoreTenant(id) {
    return apiClient.post(`/superadmin-management/tenants/${id}/restore_tenant/`)
  },
  
  getTenantAnalytics(id, params = {}) {
    return apiClient.get(`/superadmin-management/tenants/${id}/analytics/`, { params })
  },
  
  getTenantComparison(params = {}) {
    return apiClient.get('/superadmin-management/tenants/comparison/', { params })
  },
}

export default superadminAPI

