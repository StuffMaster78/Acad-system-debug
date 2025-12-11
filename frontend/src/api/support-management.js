import apiClient from './client'

export default {
  // Support Profiles
  listSupportProfiles: (params) => apiClient.get('/support-management/support-profiles/', { params }),
  getSupportProfile: (id) => apiClient.get(`/support-management/support-profiles/${id}/`),
  createSupportProfile: (data) => apiClient.post('/support-management/support-profiles/', data),
  updateSupportProfile: (id, data) => apiClient.patch(`/support-management/support-profiles/${id}/`, data),
  deleteSupportProfile: (id) => apiClient.delete(`/support-management/support-profiles/${id}/`),

  // Workload Tracker
  listWorkloadTrackers: (params) => apiClient.get('/support-management/workload-tracker/', { params }),
  getWorkloadTracker: (id) => apiClient.get(`/support-management/workload-tracker/${id}/`),
  createWorkloadTracker: (data) => apiClient.post('/support-management/workload-tracker/', data),
  updateWorkloadTracker: (id, data) => apiClient.patch(`/support-management/workload-tracker/${id}/`, data),
  deleteWorkloadTracker: (id) => apiClient.delete(`/support-management/workload-tracker/${id}/`),

  // Payment Issues
  listPaymentIssues: (params) => apiClient.get('/support-management/payment-issues/', { params }),
  getPaymentIssue: (id) => apiClient.get(`/support-management/payment-issues/${id}/`),
  createPaymentIssue: (data) => apiClient.post('/support-management/payment-issues/', data),
  updatePaymentIssue: (id, data) => apiClient.patch(`/support-management/payment-issues/${id}/`, data),
  deletePaymentIssue: (id) => apiClient.delete(`/support-management/payment-issues/${id}/`),
  escalatePaymentIssue: (id) => apiClient.post(`/support-management/payment-issues/${id}/escalate_issue/`),

  // Escalations
  listEscalations: (params) => apiClient.get('/support-management/escalations/', { params }),
  getEscalation: (id) => apiClient.get(`/support-management/escalations/${id}/`),
  createEscalation: (data) => apiClient.post('/support-management/escalations/', data),
  updateEscalation: (id, data) => apiClient.patch(`/support-management/escalations/${id}/`, data),
  deleteEscalation: (id) => apiClient.delete(`/support-management/escalations/${id}/`),
  approveEscalation: (id) => apiClient.post(`/support-management/escalations/${id}/approve/`),

  // FAQs
  listFAQs: (params) => apiClient.get('/support-management/faqs/', { params }),
  getFAQ: (id) => apiClient.get(`/support-management/faqs/${id}/`),
  createFAQ: (data) => apiClient.post('/support-management/faqs/', data),
  updateFAQ: (id, data) => apiClient.patch(`/support-management/faqs/${id}/`, data),
  deleteFAQ: (id) => apiClient.delete(`/support-management/faqs/${id}/`),
}

