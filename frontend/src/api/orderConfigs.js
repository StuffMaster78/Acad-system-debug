import apiClient from './client'

export default {
  // Order configuration endpoints - GET
  getPaperTypes: (params) => apiClient.get('/order-configs/api/paper-types/', { params }),
  getFormattingStyles: (params) => apiClient.get('/order-configs/api/formatting-styles/', { params }),
  getSubjects: (params) => apiClient.get('/order-configs/api/subjects/', { params }),
  getTypesOfWork: (params) => apiClient.get('/order-configs/api/types-of-work/', { params }),
  getEnglishTypes: (params) => apiClient.get('/order-configs/api/english-types/', { params }),
  getAcademicLevels: (params) => apiClient.get('/order-configs/api/academic-levels/', { params }),
  
  // Create endpoints
  createPaperType: (data) => apiClient.post('/order-configs/api/paper-types/', data),
  createFormattingStyle: (data) => apiClient.post('/order-configs/api/formatting-styles/', data),
  createSubject: (data) => apiClient.post('/order-configs/api/subjects/', data),
  createTypeOfWork: (data) => apiClient.post('/order-configs/api/types-of-work/', data),
  createEnglishType: (data) => apiClient.post('/order-configs/api/english-types/', data),
  createAcademicLevel: (data) => apiClient.post('/order-configs/api/academic-levels/', data),
  
  // Update endpoints
  updatePaperType: (id, data) => apiClient.put(`/order-configs/api/paper-types/${id}/`, data),
  updateFormattingStyle: (id, data) => apiClient.put(`/order-configs/api/formatting-styles/${id}/`, data),
  updateSubject: (id, data) => apiClient.put(`/order-configs/api/subjects/${id}/`, data),
  updateTypeOfWork: (id, data) => apiClient.put(`/order-configs/api/types-of-work/${id}/`, data),
  updateEnglishType: (id, data) => apiClient.put(`/order-configs/api/english-types/${id}/`, data),
  updateAcademicLevel: (id, data) => apiClient.put(`/order-configs/api/academic-levels/${id}/`, data),
  
  // Delete endpoints
  deletePaperType: (id) => apiClient.delete(`/order-configs/api/paper-types/${id}/`),
  deleteFormattingStyle: (id) => apiClient.delete(`/order-configs/api/formatting-styles/${id}/`),
  deleteSubject: (id) => apiClient.delete(`/order-configs/api/subjects/${id}/`),
  deleteTypeOfWork: (id) => apiClient.delete(`/order-configs/api/types-of-work/${id}/`),
  deleteEnglishType: (id) => apiClient.delete(`/order-configs/api/english-types/${id}/`),
  deleteAcademicLevel: (id) => apiClient.delete(`/order-configs/api/academic-levels/${id}/`),
  
  // Management endpoints
  populateDefaults: (websiteId, defaultSet = 'general') => apiClient.post('/order-configs/api/management/populate-defaults/', { website_id: websiteId, default_set: defaultSet }),
  checkDefaults: (websiteId) => apiClient.get(`/order-configs/api/management/check-defaults/?website_id=${websiteId}`),
  getAvailableDefaultSets: () => apiClient.get('/order-configs/api/management/available-default-sets/'),
  cloneFromDefaults: (websiteId, defaultSet, clearExisting = false) => apiClient.post('/order-configs/api/management/clone-from-defaults/', { 
    website_id: websiteId, 
    default_set: defaultSet,
    clear_existing: clearExisting 
  }),
  previewClone: (websiteId, defaultSet, clearExisting = false) => apiClient.post('/order-configs/api/management/preview-clone/', {
    website_id: websiteId,
    default_set: defaultSet,
    clear_existing: clearExisting
  }),
  getUsageAnalytics: (websiteId) => apiClient.get(`/order-configs/api/management/usage-analytics/?website_id=${websiteId}`),
  bulkDelete: (configType, ids, websiteId = null) => apiClient.post('/order-configs/api/management/bulk-delete/', {
    config_type: configType,
    ids: ids,
    website_id: websiteId
  }),
  exportConfigs: (websiteId) => apiClient.get(`/order-configs/api/management/export/?website_id=${websiteId}`),
  importConfigs: (websiteId, configurations, skipExisting = true) => apiClient.post('/order-configs/api/management/import/', {
    website_id: websiteId,
    configurations: configurations,
    skip_existing: skipExisting
  }),
  
  // Writer Deadline Configs
  getWriterDeadlineConfigs: (params) => apiClient.get('/order-configs/api/writer-deadline-configs/', { params }),
  createWriterDeadlineConfig: (data) => apiClient.post('/order-configs/api/writer-deadline-configs/', data),
  updateWriterDeadlineConfig: (id, data) => apiClient.put(`/order-configs/api/writer-deadline-configs/${id}/`, data),
  deleteWriterDeadlineConfig: (id) => apiClient.delete(`/order-configs/api/writer-deadline-configs/${id}/`),
}

