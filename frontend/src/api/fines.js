import apiClient from './client'

export default {
  listFines: (params) => apiClient.get('/fines/fines/', { params }),
  getFine: (id) => apiClient.get(`/fines/fines/${id}/`),
  disputeFine: (id, data) => apiClient.post(`/fines/fines/${id}/dispute/`, data),
  issue: (data) => apiClient.post('/fines/fines/issue/', data),
  listAppeals: (params) => apiClient.get('/fines/fine-appeals/', { params }),
  getAppeal: (id) => apiClient.get(`/fines/fine-appeals/${id}/`),
  getAppealTimeline: (appealId) => apiClient.get(`/fines/fine-appeals/${appealId}/timeline/`),
  postAppealComment: (appealId, data) => apiClient.post(`/fines/fine-appeals/${appealId}/timeline/`, data),
  uploadAppealEvidence: (appealId, formData) =>
    apiClient.post(`/fines/fine-appeals/${appealId}/evidence/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  listFineTypes: (params) => apiClient.get('/fines/fine-types/', { params }),
  getFineType: (id) => apiClient.get(`/fines/fine-types/${id}/`),
  createFineType: (data) => apiClient.post('/fines/fine-types/', data),
  updateFineType: (id, data) => apiClient.patch(`/fines/fine-types/${id}/`, data),
  deleteFineType: (id) => apiClient.delete(`/fines/fine-types/${id}/`),
  listLatenessRules: (params) => apiClient.get('/fines/lateness-rules/', { params }),
  getLatenessRule: (id) => apiClient.get(`/fines/lateness-rules/${id}/`),
  createLatenessRule: (data) => apiClient.post('/fines/lateness-rules/', data),
  updateLatenessRule: (id, data) => apiClient.patch(`/fines/lateness-rules/${id}/`, data),
  deleteLatenessRule: (id) => apiClient.delete(`/fines/lateness-rules/${id}/`),
  
  // Statistics
  getStatistics: (params) => apiClient.get('/fines/fines/statistics/', { params }),
  
  // Fine actions
  waiveFine: (id, data) => apiClient.post(`/fines/fines/${id}/waive/`, data),
  voidFine: (id, data) => apiClient.post(`/fines/fines/${id}/void/`, data),
  
  // Appeal actions
  reviewAppeal: (appealId, data) => apiClient.post(`/fines/fine-appeals/${appealId}/review/`, data),
}

