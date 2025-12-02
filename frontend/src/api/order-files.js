import apiClient from './client'

export default {
  // Order Files
  list: (params) => apiClient.get('/order-files/order-files/', { params }),
  get: (id) => apiClient.get(`/order-files/order-files/${id}/`),
  upload: (data) => apiClient.post('/order-files/order-files/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => apiClient.delete(`/order-files/order-files/${id}/`),
  download: (id) => apiClient.get(`/order-files/order-files/${id}/download/`),
  getSignedUrl: (id) => apiClient.get(`/order-files/order-files/${id}/signed-url/`),
  toggleDownload: (id) => apiClient.post(`/order-files/order-files/${id}/toggle_download/`),
  
  // Extra Service Files
  listExtraServiceFiles: (params) => apiClient.get('/order-files/extra-service-files/', { params }),
  getExtraServiceFile: (id) => apiClient.get(`/order-files/extra-service-files/${id}/`),
  uploadExtraServiceFile: (data) => apiClient.post('/order-files/extra-service-files/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteExtraServiceFile: (id) => apiClient.delete(`/order-files/extra-service-files/${id}/`),
  toggleExtraServiceDownload: (id) => apiClient.post(`/order-files/extra-service-files/${id}/toggle_download/`),
  
  // External File Links
  listExternalLinks: (params) => apiClient.get('/order-files/external-links/', { params }),
  getExternalLink: (id) => apiClient.get(`/order-files/external-links/${id}/`),
  createExternalLink: (data) => apiClient.post('/order-files/external-links/', data),
  updateExternalLink: (id, data) => apiClient.patch(`/order-files/external-links/${id}/`, data),
  deleteExternalLink: (id) => apiClient.delete(`/order-files/external-links/${id}/`),
  approveExternalLink: (id) => apiClient.post(`/order-files/external-links/${id}/approve/`),
  rejectExternalLink: (id) => apiClient.post(`/order-files/external-links/${id}/reject/`),
  
  // File Deletion Requests
  listDeletionRequests: (params) => apiClient.get('/order-files/file-deletion-requests/', { params }),
  getDeletionRequest: (id) => apiClient.get(`/order-files/file-deletion-requests/${id}/`),
  createDeletionRequest: (data) => apiClient.post('/order-files/file-deletion-requests/', data),
  approveDeletionRequest: (id) => apiClient.post(`/order-files/file-deletion-requests/${id}/approve/`),
  deleteDeletionRequest: (id) => apiClient.delete(`/order-files/file-deletion-requests/${id}/`),
  
  // Order Files Config
  listConfigs: (params) => apiClient.get('/order-files/order-files-config/', { params }),
  getConfig: (id) => apiClient.get(`/order-files/order-files-config/${id}/`),
  createConfig: (data) => apiClient.post('/order-files/order-files-config/', data),
  updateConfig: (id, data) => apiClient.patch(`/order-files/order-files-config/${id}/`, data),
  deleteConfig: (id) => apiClient.delete(`/order-files/order-files-config/${id}/`),
  
  // File Categories
  listCategories: (params) => apiClient.get('/order-files/file-categories/', { params }),
  getCategory: (id) => apiClient.get(`/order-files/file-categories/${id}/`),
  createCategory: (data) => apiClient.post('/order-files/file-categories/', data),
  updateCategory: (id, data) => apiClient.patch(`/order-files/file-categories/${id}/`, data),
  deleteCategory: (id) => apiClient.delete(`/order-files/file-categories/${id}/`),
}

