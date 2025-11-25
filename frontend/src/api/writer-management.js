import apiClient from './client'

export default {
  // Writer Level Configs (criteria-based levels)
  listWriterLevelConfigs: (params) => apiClient.get('/writer-management/writer-level-configs/', { params }),
  getWriterLevelConfig: (id) => apiClient.get(`/writer-management/writer-level-configs/${id}/`),
  createWriterLevelConfig: (data) => apiClient.post('/writer-management/writer-level-configs/', data),
  updateWriterLevelConfig: (id, data) => apiClient.patch(`/writer-management/writer-level-configs/${id}/`, data),
  deleteWriterLevelConfig: (id) => apiClient.delete(`/writer-management/writer-level-configs/${id}/`),
  // Writers
  listWriters: (params) => apiClient.get('/writer-management/writers/', { params }),
  getWriter: (id) => apiClient.get(`/writer-management/writers/${id}/`),
  
  // Writer Strikes
  listStrikes: (params) => apiClient.get('/writer-management/writer-strikes/', { params }),
  getStrike: (id) => apiClient.get(`/writer-management/writer-strikes/${id}/`),
  createStrike: (data) => apiClient.post('/writer-management/writer-strikes/', data),
  revokeStrike: (id) => apiClient.post(`/writer-management/writer-strikes/${id}/revoke/`),
  getStrikesByWriter: (writerId) => apiClient.get(`/writer-management/writer-strikes/by-writer/${writerId}/`),
  
  // Writer Discipline Config
  listDisciplineConfigs: (params) => apiClient.get('/writer-management/writer-discipline-configs/', { params }),
  getDisciplineConfig: (websiteId) => apiClient.get(`/writer-management/writer-discipline-configs/${websiteId}/`),
  getDisciplineConfigByWebsite: (websiteId) => apiClient.get(`/writer-management/writer-discipline-configs/by-website/${websiteId}/`),
  createDisciplineConfig: (data) => apiClient.post('/writer-management/writer-discipline-configs/', data),
  updateDisciplineConfig: (websiteId, data) => apiClient.patch(`/writer-management/writer-discipline-configs/${websiteId}/`, data),
  
  // Writer Warnings
  listWarnings: (params) => apiClient.get('/writer-management/writer-warnings/', { params }),
  getWarning: (id) => apiClient.get(`/writer-management/writer-warnings/${id}/`),
  createWarning: (data) => apiClient.post('/writer-management/writer-warnings/', data),
  deactivateWarning: (id) => apiClient.delete(`/writer-management/writer-warnings/${id}/`),
  
  // Writer Status
  getWriterStatus: (writerId) => apiClient.get(`/writer-management/writer-status/${writerId}/`),
  listWriterStatuses: (params) => apiClient.get('/writer-management/writer-status/', { params }),
}

