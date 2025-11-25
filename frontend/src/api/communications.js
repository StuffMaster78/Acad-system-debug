import apiClient from './client'

export default {
  // Threads
  listThreads: (params) => apiClient.get('/order-communications/communication-threads/', { params }),
  getThread: (threadId) => apiClient.get(`/order-communications/communication-threads/${threadId}/`),
  createThread: (data) => apiClient.post('/order-communications/communication-threads/', data),
  /**
   * Simplified method to start a conversation for an order.
   * Automatically determines participants based on order.
   * 
   * @param {number} orderId - The order ID
   * @returns {Promise} API response with thread data
   */
  startThreadForOrder: (orderId) => apiClient.post('/order-communications/communication-threads/start-for-order/', { order_id: orderId }),
  updateThread: (threadId, data) => apiClient.patch(`/order-communications/communication-threads/${threadId}/`, data),
  deleteThread: (threadId) => apiClient.delete(`/order-communications/communication-threads/${threadId}/`),
  
  // Messages
  listMessages: (threadId, params) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/`, { params }),
  getMessage: (threadId, messageId) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/`),
  sendMessage: (threadId, data) => {
    const formData = new FormData()
    formData.append('recipient_id', data.recipient_id)
    formData.append('message', data.message)
    if (data.message_type) formData.append('message_type', data.message_type)
    if (data.attachment) formData.append('attachment', data.attachment)
    if (data.is_internal_note !== undefined) formData.append('is_internal_note', data.is_internal_note)
    return apiClient.post(`/order-communications/communication-threads/${threadId}/communication-messages/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  updateMessage: (threadId, messageId, data) => apiClient.patch(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/`, data),
  deleteMessage: (threadId, messageId) => apiClient.delete(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/`),
  downloadAttachment: (threadId, messageId) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/download_attachment/`, { responseType: 'blob' }),
  getAvailableRecipients: (threadId) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/available_recipients/`),
  getOrderRecipients: (orderId) => apiClient.get(`/order-communications/communication-threads/order-recipients/`, { params: { order_id: orderId } }),
  
  // Notifications
  listNotifications: (params) => apiClient.get('/order-communications/communication-notifications/', { params }),
  markNotificationRead: (notificationId) => apiClient.patch(`/order-communications/communication-notifications/${notificationId}/`, { is_read: true }),
}
