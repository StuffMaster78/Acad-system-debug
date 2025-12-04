import apiClient from './client'

export default {
  list(params = {}) {
    return apiClient.get('/blog_pages_management/authors/', { params })
  },
  get(id) {
    return apiClient.get(`/blog_pages_management/authors/${id}/`)
  },
  create(payload) {
    // Handle FormData for file uploads
    const headers = payload instanceof FormData 
      ? { 'Content-Type': 'multipart/form-data' }
      : { 'Content-Type': 'application/json' }
    return apiClient.post('/blog_pages_management/authors/', payload, { headers })
  },
  update(id, payload) {
    // Handle FormData for file uploads
    const headers = payload instanceof FormData 
      ? { 'Content-Type': 'multipart/form-data' }
      : { 'Content-Type': 'application/json' }
    return apiClient.patch(`/blog_pages_management/authors/${id}/`, payload, { headers })
  },
  delete(id) {
    return apiClient.delete(`/blog_pages_management/authors/${id}/`)
  },
}


