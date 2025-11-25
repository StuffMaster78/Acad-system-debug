import apiClient from './client'

export default {
  // Websites
  listWebsites: (params) => apiClient.get('/websites/', { params }),
  getWebsite: (id) => apiClient.get(`/websites/${id}/`),
  createWebsite: (data) => apiClient.post('/websites/', data),
  updateWebsite: (id, data) => apiClient.put(`/websites/${id}/`, data),
  patchWebsite: (id, data) => apiClient.patch(`/websites/${id}/`, data),
  deleteWebsite: (id) => apiClient.delete(`/websites/${id}/`),
  
  // Website Actions
  updateSEOSettings: (id, data) => apiClient.patch(`/websites/${id}/update_seo_settings/`, data),
  softDeleteWebsite: (id) => apiClient.post(`/websites/${id}/soft_delete/`),
  restoreWebsite: (id) => apiClient.post(`/websites/${id}/restore/`),
  
  // Website Action Logs
  getActionLogs: (params) => apiClient.get('/websites/website-logs/', { params }),
  
  // Static Pages
  listStaticPages: (params) => apiClient.get('/websites/static-pages/', { params }),
  getStaticPage: (slug) => apiClient.get(`/websites/static-pages/${slug}/`),
}

