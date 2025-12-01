import apiClient from './client'

const writerAdvanceAPI = {
  // Get eligibility information
  getEligibility: (params) => 
    apiClient.get('/writer-management/advance-payments/eligibility/', { params }),
  
  // Request advance
  requestAdvance: (data) =>
    apiClient.post('/writer-management/advance-payments/request_advance/', data),
  
  // List requests
  listRequests: (params) =>
    apiClient.get('/writer-management/advance-payments/', { params }),
  
  // Get single request
  getRequest: (id) =>
    apiClient.get(`/writer-management/advance-payments/${id}/`),
  
  // Admin actions
  approve: (id, data) =>
    apiClient.post(`/writer-management/advance-payments/${id}/approve/`, data),
  
  reject: (id, data) =>
    apiClient.post(`/writer-management/advance-payments/${id}/reject/`, data),
  
  disburse: (id) =>
    apiClient.post(`/writer-management/advance-payments/${id}/disburse/`),
}

export default writerAdvanceAPI

