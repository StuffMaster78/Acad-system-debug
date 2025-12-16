import apiClient from './client'

export default {
  // Service Pages
  listServicePages: (params) => apiClient.get('/service-pages/service-pages/', { params }),
  getServicePage: (id) => apiClient.get(`/service-pages/service-pages/${id}/`),
  createServicePage: (data) => apiClient.post('/service-pages/service-pages/', data),
  updateServicePage: (id, data) => apiClient.put(`/service-pages/service-pages/${id}/`, data),
  patchServicePage: (id, data) => apiClient.patch(`/service-pages/service-pages/${id}/`, data),
  deleteServicePage: (id) => apiClient.delete(`/service-pages/service-pages/${id}/`),
  
  // Service Page Actions
  publishServicePage: (id) => apiClient.post(`/service-pages/service-pages/${id}/publish/`),
  unpublishServicePage: (id) => apiClient.post(`/service-pages/service-pages/${id}/unpublish/`),
  
  // PDF Sample Sections
  listPDFSampleSections: (params) => apiClient.get('/service-pages/service-page-pdf-sample-sections/', { params }),
  getPDFSampleSection: (id) => apiClient.get(`/service-pages/service-page-pdf-sample-sections/${id}/`),
  createPDFSampleSection: (data) => apiClient.post('/service-pages/service-page-pdf-sample-sections/', data),
  updatePDFSampleSection: (id, data) => apiClient.put(`/service-pages/service-page-pdf-sample-sections/${id}/`, data),
  deletePDFSampleSection: (id) => apiClient.delete(`/service-pages/service-page-pdf-sample-sections/${id}/`),
  
  // PDF Samples
  listPDFSamples: (params) => apiClient.get('/service-pages/service-page-pdf-samples/', { params }),
  getPDFSample: (id) => apiClient.get(`/service-pages/service-page-pdf-samples/${id}/`),
  createPDFSample: (data) => apiClient.post('/service-pages/service-page-pdf-samples/', data),
  updatePDFSample: (id, data) => apiClient.put(`/service-pages/service-page-pdf-samples/${id}/`, data),
  deletePDFSample: (id) => apiClient.delete(`/service-pages/service-page-pdf-samples/${id}/`),
  
  // Service Website Metrics
  listWebsiteMetrics: (params) => apiClient.get('/service-pages/service-website-metrics/', { params }),
  getLatestWebsiteMetrics: (params) => apiClient.get('/service-pages/service-website-metrics/latest/', { params }),
  recalculateWebsiteMetrics: (data) => apiClient.post('/service-pages/service-website-metrics/recalculate/', data),
}

