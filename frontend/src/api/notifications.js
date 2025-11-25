import apiClient from './client'

export default {
  getPreferences: () => apiClient.get('/notifications_system/preferences/'),
  updatePreferences: (data) => apiClient.patch('/notifications_system/preferences/', data),
  // Get notifications with user status (is_read, pinned, etc.)
  // Using the feed viewset endpoint which returns NotificationFeedItemSerializer
  getNotifications: (params) => apiClient.get('/notifications_system/notifications/feed/', { params }),
  // Alternative: get notifications without user status
  getNotificationsList: (params) => apiClient.get('/notifications_system/notifications/', { params }),
  getNotification: (id) => apiClient.get(`/notifications_system/notifications/${id}/`),
  // Mark notification as read using status ID
  markAsRead: (statusId) => apiClient.patch(`/notifications_system/notifications/status/${statusId}/mark/`, { read: true }),
  // Alternative: mark by notification ID
  markNotificationAsRead: (notificationId) => apiClient.post(`/notifications_system/mark-read/${notificationId}/`),
  markAllAsRead: () => apiClient.post('/notifications_system/mark-all-read/'),
  getUnreadCount: () => apiClient.get('/notifications_system/unread-count/'),
  getUnread: (params) => apiClient.get('/notifications_system/notifications/unread/', { params }),
}

