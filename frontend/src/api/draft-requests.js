import apiClient from './client'

export default {
  // Draft Requests
  listDraftRequests: (params) => apiClient.get('/orders/draft-requests/', { params }),
  getDraftRequest: (id) => apiClient.get(`/orders/draft-requests/${id}/`),
  createDraftRequest: (data) => apiClient.post('/orders/draft-requests/', data),
  cancelDraftRequest: (id) => apiClient.post(`/orders/draft-requests/${id}/cancel/`),
  checkEligibility: (orderId) => apiClient.get('/orders/draft-requests/check-eligibility/', {
    params: { order_id: orderId }
  }),
  
  // Draft Files
  listDraftFiles: (params) => apiClient.get('/orders/draft-files/', { params }),
  getDraftFile: (id) => apiClient.get(`/orders/draft-files/${id}/`),
  downloadDraftFile: (id) => apiClient.get(`/orders/draft-files/${id}/download/`, {
    responseType: 'blob'
  }),
  
  // Writer actions
  uploadDraft: (requestId, formData) => apiClient.post(
    `/orders/draft-requests/${requestId}/upload-draft/`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  ),
  markFulfilled: (requestId) => apiClient.post(`/orders/draft-requests/${requestId}/mark-fulfilled/`),
}

