import apiClient from './client'

export default {
  listFines: (params) => apiClient.get('/fines/api/fines/', { params }),
  getFine: (id) => apiClient.get(`/fines/api/fines/${id}/`),
  disputeFine: (id, data) => apiClient.post(`/fines/api/fines/${id}/dispute/`, data),
  issue: (data) => apiClient.post('/fines/api/fines/issue/', data),
  listAppeals: (params) => apiClient.get('/fines/api/fine-appeals/', { params }),
  getAppeal: (id) => apiClient.get(`/fines/api/fine-appeals/${id}/`),
  getAppealTimeline: (appealId) => apiClient.get(`/fines/api/fine-appeals/${appealId}/timeline/`),
  postAppealComment: (appealId, data) => apiClient.post(`/fines/api/fine-appeals/${appealId}/timeline/`, data),
  uploadAppealEvidence: (appealId, formData) =>
    apiClient.post(`/fines/api/fine-appeals/${appealId}/evidence/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  listFineTypes: (params) => apiClient.get('/fines/api/fine-types/', { params }),
  getFineType: (id) => apiClient.get(`/fines/api/fine-types/${id}/`),
  createFineType: (data) => apiClient.post('/fines/api/fine-types/', data),
  updateFineType: (id, data) => apiClient.patch(`/fines/api/fine-types/${id}/`, data),
  deleteFineType: (id) => apiClient.delete(`/fines/api/fine-types/${id}/`),
  listLatenessRules: (params) => apiClient.get('/fines/api/lateness-rules/', { params }),
  getLatenessRule: (id) => apiClient.get(`/fines/api/lateness-rules/${id}/`),
  createLatenessRule: (data) => apiClient.post('/fines/api/lateness-rules/', data),
  updateLatenessRule: (id, data) => apiClient.patch(`/fines/api/lateness-rules/${id}/`, data),
  deleteLatenessRule: (id) => apiClient.delete(`/fines/api/lateness-rules/${id}/`),
}

