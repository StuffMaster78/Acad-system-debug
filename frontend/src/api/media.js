import apiClient from './client'

export default {
  // Media Assets
  list: (params) => apiClient.get('/media/media-assets/', { params }),
  get: (id) => apiClient.get(`/media/media-assets/${id}/`),
  create: (data) => apiClient.post('/media/media-assets/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id, data) => apiClient.put(`/media/media-assets/${id}/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  patch: (id, data) => apiClient.patch(`/media/media-assets/${id}/`, data),
  delete: (id) => apiClient.delete(`/media/media-assets/${id}/`),
  
  // Media Types
  getAllTypes: () => apiClient.get('/media/media-assets/types/'),
}

