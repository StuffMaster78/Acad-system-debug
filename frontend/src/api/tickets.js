import apiClient from './client'

function toFormData(payload) {
  const fd = new FormData()
  Object.entries(payload || {}).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return
    if (k === 'attachments' && Array.isArray(v)) {
      v.forEach((file) => fd.append('attachments', file))
    } else {
      fd.append(k, v)
    }
  })
  return fd
}

export default {
  list: (params) => apiClient.get('/tickets/tickets/', { params }),
  get: (id) => apiClient.get(`/tickets/tickets/${id}/`),
  create: (payload) => apiClient.post('/tickets/tickets/', toFormData(payload), {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (id, payload) => apiClient.patch(`/tickets/tickets/${id}/`, payload),
  thread: (id) => apiClient.get(`/tickets/tickets/${id}/thread/`),
  reply: (id, payload) => apiClient.post(`/tickets/tickets/${id}/reply/`, toFormData(payload), {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  close: (id, reason = '') => apiClient.post(`/tickets/tickets/${id}/close/`, { reason }),
  reopen: (id, reason = '', status = 'open') => apiClient.post(`/tickets/tickets/${id}/reopen/`, { reason, status }),
  assign: (id, assignedToId) => apiClient.post(`/tickets/tickets/${id}/assign/`, { assigned_to: assignedToId }),
  escalate: (id) => apiClient.post(`/tickets/tickets/${id}/escalate/`),
}
