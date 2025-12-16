import apiClient from './client'

export default {
  // Websites
  listWebsites: (params) => apiClient.get('/websites/websites/', { params }),
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
  /**
   * List static pages for a website.
   * Expected params:
   *  - website: domain (optional if X-Website header is set)
   *  - lang: language code (e.g. 'en')
   */
  listStaticPages: (params) => apiClient.get('/websites/static-pages/', { params }),

  /**
   * Get a specific static page by slug.
   * Optionally accepts params (e.g. website, lang).
   */
  getStaticPage: (slug, params = {}) =>
    apiClient.get(`/websites/static-pages/${slug}/`, { params }),

  /**
   * Update Terms & Conditions (admin-only).
   * This calls the backend WebsiteViewSet `update_terms` action.
   */
  updateTerms: (websiteId, data) =>
    apiClient.post(`/websites/${websiteId}/update_terms/`, data),
}

