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
  thread: (id) => apiClient.get(`/tickets/tickets/${id}/thread/`),
  reply: (id, payload) => apiClient.post(`/tickets/tickets/${id}/reply/`, toFormData(payload), {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
}
