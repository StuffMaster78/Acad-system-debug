import apiClient from './client'

export default {
  list: (params) => apiClient.get('/activity/activity-logs/', { params }),
  get: (id) => apiClient.get(`/activity/activity-logs/${id}/`),
}

