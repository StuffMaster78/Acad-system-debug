import apiClient from './client'

export default {
  // Admin Activity Logs (admin-specific actions)
  listAdminLogs: (params) => apiClient.get('/admin-management/activity-logs/', { params }),
  getAdminLog: (id) => apiClient.get(`/admin-management/activity-logs/${id}/`),
  
  // General Activity Logs (comprehensive, all activities)
  // Note: This endpoint may not exist if activity app URLs aren't included
  // Will gracefully handle 404 if endpoint doesn't exist
  list: (params) => apiClient.get('/activity/activity-logs/', { params }).catch(() => ({ data: { results: [], count: 0 } })),
  get: (id) => apiClient.get(`/activity/activity-logs/${id}/`),
  
  // Note: Activity logs are read-only, no create/update/delete operations
}

