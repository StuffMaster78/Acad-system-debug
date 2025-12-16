import apiClient from './client'

export default {
  // ===== SEO Landing Pages (new SeoPage model) =====
  // Admin endpoints
  list: (params) => apiClient.get('/seo-pages/seo-pages/', { params }),
  get: (id) => apiClient.get(`/seo-pages/seo-pages/${id}/`),
  create: (data) => apiClient.post('/seo-pages/seo-pages/', data),
  update: (id, data) => apiClient.put(`/seo-pages/seo-pages/${id}/`, data),
  patch: (id, data) => apiClient.patch(`/seo-pages/seo-pages/${id}/`, data),
  delete: (id) => apiClient.delete(`/seo-pages/seo-pages/${id}/`),
  preview: (id) => apiClient.get(`/seo-pages/seo-pages/${id}/preview/`),
  
  // Public endpoints
  getBySlug: (slug, params = {}) => apiClient.get(`/public/seo-pages/${slug}/`, { params }),
  listPublic: (params) => apiClient.get('/public/seo-pages/', { params }),
  
  // ===== Service Pages (existing ServicePage model) =====
  // These methods are for the ServicePage model used in SEOPagesManagement.vue
  listServicePages: (params) => apiClient.get('/service-pages/service-pages/', { params }),
  getServicePage: (id) => apiClient.get(`/service-pages/service-pages/${id}/`),
  createServicePage: (data) => apiClient.post('/service-pages/service-pages/', data),
  updateServicePage: (id, data) => apiClient.put(`/service-pages/service-pages/${id}/`, data),
  patchServicePage: (id, data) => apiClient.patch(`/service-pages/service-pages/${id}/`, data),
  deleteServicePage: (id) => apiClient.delete(`/service-pages/service-pages/${id}/`),
  
  // Helper methods
  getAvailableWebsites: () => apiClient.get('/service-pages/service-pages/available_websites/'),
  
  // Edit History
  getServicePageEditHistory: (id, params = {}) => apiClient.get(`/service-pages/service-pages/${id}/edit-history/`, { params }),
  getServicePageRevisions: (id, params = {}) => apiClient.get(`/service-pages/service-pages/${id}/revisions/`, { params }),
}
