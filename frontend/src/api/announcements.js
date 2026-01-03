/**
 * API client for announcements management
 */
import apiClient from './client'

export default {
  // Public endpoints (all users)
  listAnnouncements: (params) => apiClient.get('/announcements/announcements/', { params }),
  getAnnouncement: (id) => apiClient.get(`/announcements/announcements/${id}/`),
  trackView: (id, timeSpent) => apiClient.post(`/announcements/announcements/${id}/view/`, { time_spent: timeSpent }),
  acknowledge: (id) => apiClient.post(`/announcements/announcements/${id}/acknowledge/`),
  getUnreadCount: () => apiClient.get('/announcements/announcements/unread_count/'),

  // Admin endpoints
  createAnnouncement: (data) => apiClient.post('/announcements/announcements/', data),
  updateAnnouncement: (id, data) => apiClient.patch(`/announcements/announcements/${id}/`, data),
  deleteAnnouncement: (id) => apiClient.delete(`/announcements/announcements/${id}/`),
  pinAnnouncement: (id) => apiClient.post(`/announcements/announcements/${id}/pin/`),
  unpinAnnouncement: (id) => apiClient.post(`/announcements/announcements/${id}/unpin/`),
  getAnalytics: (id) => apiClient.get(`/announcements/announcements/${id}/analytics/`),
  getReaders: (id) => apiClient.get(`/announcements/announcements/${id}/readers/`),
  exportAnalytics: (id) => apiClient.get(`/announcements/announcements/${id}/export_analytics/`, { responseType: 'blob' }),
}

