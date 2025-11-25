import apiClient from './client'

export default {
  // Service Pages (SEO Pages)
  listServicePages: (params) => apiClient.get('/service-pages/service-pages/', { params }),
  getServicePage: (id) => apiClient.get(`/service-pages/service-pages/${id}/`),
  createServicePage: (data) => apiClient.post('/service-pages/service-pages/', data),
  updateServicePage: (id, data) => apiClient.put(`/service-pages/service-pages/${id}/`, data),
  patchServicePage: (id, data) => apiClient.patch(`/service-pages/service-pages/${id}/`, data),
  deleteServicePage: (id) => apiClient.delete(`/service-pages/service-pages/${id}/`),
  getAvailableWebsites: () => apiClient.get('/service-pages/service-pages/available_websites/'),
  
  // SEO Metadata for Service Pages
  getSEOMetadata: (id) => apiClient.get(`/service-pages/service-pages/${id}/seo-metadata/`),
  updateSEOMetadata: (id, data) => apiClient.post(`/service-pages/service-pages/${id}/seo-metadata/`, data),
  getSchema: (id) => apiClient.get(`/service-pages/service-pages/${id}/schema/`),
  getOGTags: (id) => apiClient.get(`/service-pages/service-pages/${id}/og-tags/`),
  getTwitterTags: (id) => apiClient.get(`/service-pages/service-pages/${id}/twitter-tags/`),
  
  // FAQs for Service Pages
  getFAQs: (id) => apiClient.get(`/service-pages/service-pages/${id}/faqs/`),
  createFAQ: (id, data) => apiClient.post(`/service-pages/service-pages/${id}/faqs/`, data),
  updateFAQ: (id, faqId, data) => apiClient.put(`/service-pages/service-pages/${id}/faqs/${faqId}/`, data),
  deleteFAQ: (id, faqId) => apiClient.delete(`/service-pages/service-pages/${id}/faqs/${faqId}/`),
  
  // Resources for Service Pages
  getResources: (id) => apiClient.get(`/service-pages/service-pages/${id}/resources/`),
  createResource: (id, data) => apiClient.post(`/service-pages/service-pages/${id}/resources/`, data),
  updateResource: (id, resourceId, data) => apiClient.put(`/service-pages/service-pages/${id}/resources/${resourceId}/`, data),
  deleteResource: (id, resourceId) => apiClient.delete(`/service-pages/service-pages/${id}/resources/${resourceId}/`),
  
  // CTAs for Service Pages
  getCTAs: (id) => apiClient.get(`/service-pages/service-pages/${id}/ctas/`),
  createCTA: (id, data) => apiClient.post(`/service-pages/service-pages/${id}/ctas/`, data),
  updateCTA: (id, ctaId, data) => apiClient.put(`/service-pages/service-pages/${id}/ctas/${ctaId}/`, data),
  deleteCTA: (id, ctaId) => apiClient.delete(`/service-pages/service-pages/${id}/ctas/${ctaId}/`),
  
  // Edit History
  getEditHistory: (id) => apiClient.get(`/service-pages/service-pages/${id}/edit-history/`),
  
  // PDF Samples
  listPDFSections: (params) => apiClient.get('/service-pages/service-page-pdf-sample-sections/', { params }),
  getPDFSection: (id) => apiClient.get(`/service-pages/service-page-pdf-sample-sections/${id}/`),
  createPDFSection: (data) => apiClient.post('/service-pages/service-page-pdf-sample-sections/', data),
  updatePDFSection: (id, data) => apiClient.put(`/service-pages/service-page-pdf-sample-sections/${id}/`, data),
  deletePDFSection: (id) => apiClient.delete(`/service-pages/service-page-pdf-sample-sections/${id}/`),
  
  listPDFSamples: (params) => apiClient.get('/service-pages/service-page-pdf-samples/', { params }),
  getPDFSample: (id) => apiClient.get(`/service-pages/service-page-pdf-samples/${id}/`),
  createPDFSample: (formData) => apiClient.post('/service-pages/service-page-pdf-samples/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  downloadPDFSample: (id) => apiClient.post(`/service-pages/service-page-pdf-samples/${id}/download/`),
  deletePDFSample: (id) => apiClient.delete(`/service-pages/service-page-pdf-samples/${id}/`),
}

