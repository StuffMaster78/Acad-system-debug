import apiClient from './client'

const normalizeParams = (input) => {
  if (typeof input === 'number') {
    return { days: input }
  }
  if (typeof input === 'object' && input !== null) {
    return input
  }
  return { days: 30 }
}

export default {
  getDashboardStats: (params = 30) =>
    apiClient.get('/editor-management/profiles/dashboard_stats/', { params: normalizeParams(params) }),
  getMyProfile: () => apiClient.get('/editor-management/profiles/my_profile/'),
  getTasks: (params) => apiClient.get('/editor-management/tasks/', { params }),
  getAvailableTasks: () => apiClient.get('/editor-management/tasks/available_tasks/'),
  getPerformance: () => apiClient.get('/editor-management/performance/'),
}

