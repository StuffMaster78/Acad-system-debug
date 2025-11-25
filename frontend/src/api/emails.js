/**
 * API client for email management (mass emails, digests, broadcasts)
 */
import apiClient from './client'

export default {
  // Mass Emails
  listMassEmails: (params) => apiClient.get('/admin-management/emails/mass-emails/', { params }),
  getMassEmail: (id) => apiClient.get(`/admin-management/emails/mass-emails/${id}/`),
  createMassEmail: (data) => apiClient.post('/admin-management/emails/mass-emails/', data),
  updateMassEmail: (id, data) => apiClient.patch(`/admin-management/emails/mass-emails/${id}/`, data),
  deleteMassEmail: (id) => apiClient.delete(`/admin-management/emails/mass-emails/${id}/`),
  sendMassEmailNow: (id) => apiClient.post(`/admin-management/emails/mass-emails/${id}/send_now/`),
  scheduleMassEmail: (id, scheduledTime) => apiClient.post(`/admin-management/emails/mass-emails/${id}/schedule/`, { scheduled_time: scheduledTime }),
  getMassEmailAnalytics: (id) => apiClient.get(`/admin-management/emails/mass-emails/${id}/analytics/`),

  // Email Digests
  listDigests: (params) => apiClient.get('/admin-management/emails/digests/', { params }),
  getDigest: (id) => apiClient.get(`/admin-management/emails/digests/${id}/`),
  createDigest: (data) => apiClient.post('/admin-management/emails/digests/', data),
  updateDigest: (id, data) => apiClient.patch(`/admin-management/emails/digests/${id}/`, data),
  deleteDigest: (id) => apiClient.delete(`/admin-management/emails/digests/${id}/`),
  getDigestConfigs: () => apiClient.get('/admin-management/emails/digests/configs/'),
  sendDigestNow: (id) => apiClient.post(`/admin-management/emails/digests/${id}/send_now/`),
  sendDueDigests: () => apiClient.post('/admin-management/emails/digests/send_due/'),

  // Broadcast Messages
  listBroadcasts: (params) => apiClient.get('/admin-management/emails/broadcasts/', { params }),
  getBroadcast: (id) => apiClient.get(`/admin-management/emails/broadcasts/${id}/`),
  createBroadcast: (data) => apiClient.post('/admin-management/emails/broadcasts/', data),
  updateBroadcast: (id, data) => apiClient.patch(`/admin-management/emails/broadcasts/${id}/`, data),
  deleteBroadcast: (id) => apiClient.delete(`/admin-management/emails/broadcasts/${id}/`),
  sendBroadcastNow: (id) => apiClient.post(`/admin-management/emails/broadcasts/${id}/send_now/`),
  previewBroadcast: (id) => apiClient.post(`/admin-management/emails/broadcasts/${id}/preview/`),
  getBroadcastStats: (id) => apiClient.get(`/admin-management/emails/broadcasts/${id}/stats/`),

  // Email Templates
  listTemplates: (params) => apiClient.get('/mass-emails/templates/', { params }),
  getTemplate: (id) => apiClient.get(`/mass-emails/templates/${id}/`),
  createTemplate: (data) => apiClient.post('/mass-emails/templates/', data),
  updateTemplate: (id, data) => apiClient.patch(`/mass-emails/templates/${id}/`, data),
  deleteTemplate: (id) => apiClient.delete(`/mass-emails/templates/${id}/`),
}

