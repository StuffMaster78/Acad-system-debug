import apiClient from './client'

export default {
  // Fines
  list: (params) => apiClient.get('/fines/api/fines/', { params }),
  get: (id) => apiClient.get(`/fines/api/fines/${id}/`),
  create: (data) => apiClient.post('/fines/api/fines/', data),
  update: (id, data) => apiClient.patch(`/fines/api/fines/${id}/`, data),
  delete: (id) => apiClient.delete(`/fines/api/fines/${id}/`),
  
  // Fine Actions
  issue: (data) => apiClient.post('/fines/api/fines/issue/', data),
  waive: (id, data) => apiClient.post(`/fines/api/fines/${id}/waive/`, data),
  void: (id, data) => apiClient.post(`/fines/api/fines/${id}/void/`, data),
  dispute: (id, data) => apiClient.post(`/fines/api/fines/${id}/dispute/`, data),
  getAvailableTypes: () => apiClient.get('/fines/api/fines/available-types/'),
  
  // Fine Appeals
  listAppeals: (params) => apiClient.get('/fines/api/fine-appeals/', { params }),
  getAppeal: (id) => apiClient.get(`/fines/api/fine-appeals/${id}/`),
  createAppeal: (data) => apiClient.post('/fines/api/fine-appeals/', data),
  reviewAppeal: (id, data) => apiClient.post(`/fines/api/fine-appeals/${id}/review/`, data),
  escalateAppeal: (id, data) => apiClient.post(`/fines/api/fine-appeals/${id}/escalate/`, data),
  
  // Fine Types Configuration
  listFineTypes: (params) => apiClient.get('/fines/api/fine-types/', { params }),
  getFineType: (id) => apiClient.get(`/fines/api/fine-types/${id}/`),
  createFineType: (data) => apiClient.post('/fines/api/fine-types/', data),
  updateFineType: (id, data) => apiClient.patch(`/fines/api/fine-types/${id}/`, data),
  deleteFineType: (id) => apiClient.delete(`/fines/api/fine-types/${id}/`),
  getAvailableFineTypes: () => apiClient.get('/fines/api/fine-types/available_types/'),
  
  // Lateness Rules
  listLatenessRules: (params) => apiClient.get('/fines/api/lateness-rules/', { params }),
  getLatenessRule: (id) => apiClient.get(`/fines/api/lateness-rules/${id}/`),
  createLatenessRule: (data) => apiClient.post('/fines/api/lateness-rules/', data),
  updateLatenessRule: (id, data) => apiClient.patch(`/fines/api/lateness-rules/${id}/`, data),
  deleteLatenessRule: (id) => apiClient.delete(`/fines/api/lateness-rules/${id}/`),
  getActiveLatenessRule: () => apiClient.get('/fines/api/lateness-rules/active_rule/'),
}

