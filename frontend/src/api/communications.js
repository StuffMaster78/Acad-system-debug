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
  /**
   * Create a general messaging thread (not order-related)
   * @param {number} recipientId - The recipient user ID
   * @param {string} message - Initial message text
   * @param {string} threadType - Thread type (default: 'general')
   * @returns {Promise} API response with thread data
   */
  createGeneralThread: (recipientId, message, threadType = 'general') => 
    apiClient.post('/order-communications/communication-threads/create-general-thread/', {
      recipient_id: recipientId,
      message: message,
      thread_type: threadType
    }),
  updateThread: (threadId, data) => apiClient.patch(`/order-communications/communication-threads/${threadId}/`, data),
  deleteThread: (threadId) => apiClient.delete(`/order-communications/communication-threads/${threadId}/`),
  
  // Messages
  listMessages: (threadId, params) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/`, { params }),
  getMessage: (threadId, messageId) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/`),
  sendMessage: (threadId, data) => {
    const formData = new FormData()
    // Support both 'recipient' and 'recipient_id' for backward compatibility
    const recipientId = data.recipient_id || data.recipient
    formData.append('recipient', recipientId)  // Backend expects 'recipient' as IntegerField
    formData.append('message', data.message)
    if (data.message_type) formData.append('message_type', data.message_type)
    if (data.attachment) formData.append('attachment', data.attachment)
    if (data.is_internal_note !== undefined) formData.append('is_internal_note', data.is_internal_note)
    if (data.reply_to || data.reply_to_id) {
      formData.append('reply_to', data.reply_to || data.reply_to_id)  // Backend expects 'reply_to'
    }
    return apiClient.post(`/order-communications/communication-threads/${threadId}/communication-messages/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  /**
   * Simplified message sending - auto-detects recipient
   * @param {number} threadId - The thread ID
   * @param {string} message - Message text
   * @param {File} attachment - Optional file attachment
   * @param {number} replyTo - Optional message ID to reply to
   * @returns {Promise} API response
   */
  sendMessageSimple: (threadId, message, attachment = null, replyTo = null) => {
    const formData = new FormData()
    if (message) formData.append('message', message)
    if (attachment) formData.append('attachment', attachment)
    if (replyTo) formData.append('reply_to', replyTo)
    return apiClient.post(`/order-communications/communication-threads/${threadId}/send-message-simple/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  updateMessage: (threadId, messageId, data) => apiClient.patch(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/`, data),
  deleteMessage: (threadId, messageId) => apiClient.delete(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/`),
  downloadAttachment: (threadId, messageId) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/download_attachment/`, { responseType: 'blob' }),
  uploadAttachment: (formData) => apiClient.post('/order-communications/message-attachments/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getAvailableRecipients: (threadId) => apiClient.get(`/order-communications/communication-threads/${threadId}/communication-messages/available_recipients/`),
  getOrderRecipients: (orderId) => apiClient.get(`/order-communications/communication-threads/order-recipients/`, { params: { order_id: orderId } }),
  
  // Notifications
  listNotifications: (params) => apiClient.get('/order-communications/communication-notifications/', { params }),
  markNotificationRead: (notificationId) => apiClient.patch(`/order-communications/communication-notifications/${notificationId}/`, { is_read: true }),
  
  // Enhanced features
  markMessageAsRead: (threadId, messageId) => apiClient.post(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/mark_as_read/`),
  markThreadAsRead: (threadId) => apiClient.post(`/order-communications/communication-threads/${threadId}/communication-messages/mark-thread-read/`),
  addReaction: (threadId, messageId, reaction) => apiClient.post(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/react/`, { reaction }),
  removeReaction: (threadId, messageId, reaction) => apiClient.delete(`/order-communications/communication-threads/${threadId}/communication-messages/${messageId}/react/`, { data: { reaction } }),
  setTyping: (threadId) => apiClient.post(`/order-communications/communication-threads/${threadId}/typing/`),
  getTypingStatus: (threadId) => apiClient.get(`/order-communications/communication-threads/${threadId}/typing_status/`),
  
  // Flagged Messages
  listFlaggedMessages: (params) => apiClient.get('/order-communications/flagged-messages/', { params }),
  getFlaggedMessage: (id) => apiClient.get(`/order-communications/flagged-messages/${id}/`),
  unblockFlaggedMessage: (id, data) => apiClient.post(`/order-communications/flagged-messages/${id}/unblock/`, data),
  reflagMessage: (id) => apiClient.post(`/order-communications/flagged-messages/${id}/reflag/`),
  updateFlaggedMessageCategory: (id, category) => apiClient.patch(`/order-communications/flagged-messages/${id}/update_category/`, { category }),
  editFlaggedMessage: (id, data) => apiClient.patch(`/order-communications/flagged-messages/${id}/edit/`, data),
  getFlaggedMessagesStats: () => apiClient.get('/order-communications/flagged-messages/statistics/'),
}
