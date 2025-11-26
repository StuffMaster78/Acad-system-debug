import apiClient from './client'

export default {
  // Notification Groups
  listGroups: (params) => apiClient.get('/notifications_system/notification-groups/', { params }),
  getGroup: (id) => apiClient.get(`/notifications_system/notification-groups/${id}/`),
  createGroup: (data) => apiClient.post('/notifications_system/notification-groups/', data),
  updateGroup: (id, data) => apiClient.put(`/notifications_system/notification-groups/${id}/`, data),
  patchGroup: (id, data) => apiClient.patch(`/notifications_system/notification-groups/${id}/`, data),
  deleteGroup: (id) => apiClient.delete(`/notifications_system/notification-groups/${id}/`),
  addUsersToGroup: (id, userIds) => apiClient.post(`/notifications_system/notification-groups/${id}/add-users/`, { user_ids: userIds }),
  removeUsersFromGroup: (id, userIds) => apiClient.post(`/notifications_system/notification-groups/${id}/remove-users/`, { user_ids: userIds }),

  // Notification Group Profiles
  listGroupProfiles: (params) => apiClient.get('/notifications_system/notification-group-profiles/', { params }),
  getGroupProfile: (id) => apiClient.get(`/notifications_system/notification-group-profiles/${id}/`),
  createGroupProfile: (data) => apiClient.post('/notifications_system/notification-group-profiles/', data),
  updateGroupProfile: (id, data) => apiClient.put(`/notifications_system/notification-group-profiles/${id}/`, data),
  patchGroupProfile: (id, data) => apiClient.patch(`/notifications_system/notification-group-profiles/${id}/`, data),
  deleteGroupProfile: (id) => apiClient.delete(`/notifications_system/notification-group-profiles/${id}/`),
  addUsersToGroupProfile: (id, userIds) => apiClient.post(`/notifications_system/notification-group-profiles/${id}/add-users/`, { user_ids: userIds }),
  removeUsersFromGroupProfile: (id, userIds) => apiClient.post(`/notifications_system/notification-group-profiles/${id}/remove-users/`, { user_ids: userIds }),
  setDefaultGroupProfile: (id) => apiClient.post(`/notifications_system/notification-group-profiles/${id}/set-default/`),
}

