import apiClient from './client'

export default {
  // Writer Support Tickets (using general tickets API)
  list: (params) => apiClient.get('/tickets/tickets/', { params }),
  get: (id) => apiClient.get(`/tickets/tickets/${id}/`),
  create: (data) => apiClient.post('/tickets/tickets/', data),
  update: (id, data) => apiClient.patch(`/tickets/tickets/${id}/`, data),
  
  // Ticket Messages
  listMessages: (params) => apiClient.get('/tickets/messages/', { params }),
  createMessage: (data) => apiClient.post('/tickets/messages/', data),
  
  // Ticket Attachments
  listAttachments: (params) => apiClient.get('/tickets/attachments/', { params }),
  uploadAttachment: (data) => apiClient.post('/tickets/attachments/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  downloadAttachment: (id) => apiClient.get(`/tickets/attachments/${id}/download/`, {
    responseType: 'blob'
  }),
  
  // Ticket Logs
  listLogs: (params) => apiClient.get('/tickets/logs/', { params }),
}

