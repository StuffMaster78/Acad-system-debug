import apiClient from './client'

export default {
  // Writer Profile
  getProfile: () => apiClient.get('/writer-management/writers/me/'),
  updateProfile: (data) => apiClient.patch('/writer-management/writers/me/', data),
  
  // Pen Name Change Requests
  getPenNameChangeRequests: (params) => apiClient.get('/writer-management/pen-name-change-requests/', { params }),
  createPenNameChangeRequest: (data) => apiClient.post('/writer-management/pen-name-change-requests/', data),
  getPenNameChangeRequest: (id) => apiClient.get(`/writer-management/pen-name-change-requests/${id}/`),
  
  // Writer Resources
  getResources: (params) => apiClient.get('/writer-management/writer-resources/', { params }),
  getResource: (id) => apiClient.get(`/writer-management/writer-resources/${id}/`),
  trackResourceView: (id) => apiClient.post(`/writer-management/writer-resources/${id}/view/`),
  downloadResource: (id) => apiClient.post(`/writer-management/writer-resources/${id}/download/`),
  
  // Resource Categories
  getResourceCategories: (params) => apiClient.get('/writer-management/writer-resource-categories/', { params }),
}

