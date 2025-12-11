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
  getDropdownOptions: (params) => apiClient.get('/order-configs/api/management/dropdown-options/', { params }),
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
  
  // Subject Templates
  getSubjectTemplates: (params) => apiClient.get('/order-configs/api/subject-templates/', { params }),
  getSubjectTemplate: (id) => apiClient.get(`/order-configs/api/subject-templates/${id}/`),
  createSubjectTemplate: (data) => apiClient.post('/order-configs/api/subject-templates/', data),
  updateSubjectTemplate: (id, data) => apiClient.patch(`/order-configs/api/subject-templates/${id}/`, data),
  deleteSubjectTemplate: (id) => apiClient.delete(`/order-configs/api/subject-templates/${id}/`),
  cloneSubjectTemplateToWebsite: (templateId, websiteId, skipExisting = true) => apiClient.post(
    `/order-configs/api/subject-templates/${templateId}/clone-to-website/`,
    { website_id: websiteId, skip_existing: skipExisting }
  ),
  getSubjectTemplateCategories: () => apiClient.get('/order-configs/api/subject-templates/categories/'),
  
  // Paper Type Templates
  getPaperTypeTemplates: (params) => apiClient.get('/order-configs/api/paper-type-templates/', { params }),
  getPaperTypeTemplate: (id) => apiClient.get(`/order-configs/api/paper-type-templates/${id}/`),
  createPaperTypeTemplate: (data) => apiClient.post('/order-configs/api/paper-type-templates/', data),
  updatePaperTypeTemplate: (id, data) => apiClient.patch(`/order-configs/api/paper-type-templates/${id}/`, data),
  deletePaperTypeTemplate: (id) => apiClient.delete(`/order-configs/api/paper-type-templates/${id}/`),
  clonePaperTypeTemplateToWebsite: (templateId, websiteId, skipExisting = true) => apiClient.post(
    `/order-configs/api/paper-type-templates/${templateId}/clone-to-website/`,
    { website_id: websiteId, skip_existing: skipExisting }
  ),
  getPaperTypeTemplateCategories: () => apiClient.get('/order-configs/api/paper-type-templates/categories/'),
  
  // Type of Work Templates
  getTypeOfWorkTemplates: (params) => apiClient.get('/order-configs/api/type-of-work-templates/', { params }),
  getTypeOfWorkTemplate: (id) => apiClient.get(`/order-configs/api/type-of-work-templates/${id}/`),
  createTypeOfWorkTemplate: (data) => apiClient.post('/order-configs/api/type-of-work-templates/', data),
  updateTypeOfWorkTemplate: (id, data) => apiClient.patch(`/order-configs/api/type-of-work-templates/${id}/`, data),
  deleteTypeOfWorkTemplate: (id) => apiClient.delete(`/order-configs/api/type-of-work-templates/${id}/`),
  cloneTypeOfWorkTemplateToWebsite: (templateId, websiteId, skipExisting = true) => apiClient.post(
    `/order-configs/api/type-of-work-templates/${templateId}/clone-to-website/`,
    { website_id: websiteId, skip_existing: skipExisting }
  ),
  getTypeOfWorkTemplateCategories: () => apiClient.get('/order-configs/api/type-of-work-templates/categories/'),
}

