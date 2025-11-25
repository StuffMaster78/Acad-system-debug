import apiClient from './client'

export default {
  // Tasks
  list: (params) => apiClient.get('/editor-management/tasks/', { params }),
  get: (id) => apiClient.get(`/editor-management/tasks/${id}/`),
  
  // Available Tasks
  getAvailableTasks: (params) => apiClient.get('/editor-management/tasks/available_tasks/', { params }),
  
  // Task Actions
  claim: (data) => apiClient.post('/editor-management/tasks/claim/', data),
  startReview: (id, data) => apiClient.post(`/editor-management/tasks/${id}/start_review/`, data),
  submitReview: (data) => apiClient.post('/editor-management/tasks/submit_review/', data),
  completeTask: (data) => apiClient.post('/editor-management/tasks/complete_task/', data),
  rejectTask: (data) => apiClient.post('/editor-management/tasks/reject_task/', data),
  unclaim: (data) => apiClient.post('/editor-management/tasks/unclaim/', data),
  
  // Dashboard Stats
  getDashboardStats: (params) => apiClient.get('/editor-management/profiles/dashboard_stats/', { params }),
}

