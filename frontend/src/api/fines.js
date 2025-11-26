import apiClient from './client'

export default {
  listFines: (params) => apiClient.get('/fines/api/fines/', { params }),
  getFine: (id) => apiClient.get(`/fines/api/fines/${id}/`),
  disputeFine: (id, data) => apiClient.post(`/fines/api/fines/${id}/dispute/`, data),
  listAppeals: (params) => apiClient.get('/fines/api/fine-appeals/', { params }),
  getAppeal: (id) => apiClient.get(`/fines/api/fine-appeals/${id}/`),
  getAppealTimeline: (appealId) => apiClient.get(`/fines/api/fine-appeals/${appealId}/timeline/`),
  postAppealComment: (appealId, data) => apiClient.post(`/fines/api/fine-appeals/${appealId}/timeline/`, data),
  uploadAppealEvidence: (appealId, formData) =>
    apiClient.post(`/fines/api/fine-appeals/${appealId}/evidence/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
}

