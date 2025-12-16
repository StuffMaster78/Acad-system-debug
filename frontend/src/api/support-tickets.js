import apiClient from './client'

export default {
  // Tickets
  list: (params) => apiClient.get('/tickets/tickets/', { params }),
  get: (id) => apiClient.get(`/tickets/tickets/${id}/`),
  create: (data) => apiClient.post('/tickets/tickets/', data),
  update: (id, data) => apiClient.patch(`/tickets/tickets/${id}/`, data),
  delete: (id) => apiClient.delete(`/tickets/tickets/${id}/`),
  
  // Ticket Actions
  assign: (id, data) => apiClient.post(`/tickets/tickets/${id}/assign/`, data),
  escalate: (id) => apiClient.post(`/tickets/tickets/${id}/escalate/`),
  
  // Ticket Messages
  listMessages: (params) => apiClient.get('/tickets/messages/', { params }),
  getMessage: (id) => apiClient.get(`/tickets/messages/${id}/`),
  createMessage: (data) => apiClient.post('/tickets/messages/', data),
  updateMessage: (id, data) => apiClient.patch(`/tickets/messages/${id}/`, data),
  deleteMessage: (id) => apiClient.delete(`/tickets/messages/${id}/`),
  
  // Ticket Attachments
  listAttachments: (params) => apiClient.get('/tickets/attachments/', { params }),
  getAttachment: (id) => apiClient.get(`/tickets/attachments/${id}/`),
  uploadAttachment: (data) => apiClient.post('/tickets/attachments/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  downloadAttachment: (id) => apiClient.get(`/tickets/attachments/${id}/download/`, {
    responseType: 'blob'
  }),
  deleteAttachment: (id) => apiClient.delete(`/tickets/attachments/${id}/`),
  
  // Ticket Logs
  listLogs: (params) => apiClient.get('/tickets/logs/', { params }),
  getLog: (id) => apiClient.get(`/tickets/logs/${id}/`),
  
  // Ticket Statistics (backend exposes /statistics/generate/)
  getStatistics: (params) => apiClient.get('/tickets/statistics/generate/', { params }),
}

