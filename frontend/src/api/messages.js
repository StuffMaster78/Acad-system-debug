import apiClient from './client'
import communications from './communications'

/**
 * Messages API
 * Simplified interface for message-related operations
 * Wraps the communications API for common use cases
 */
export default {
  /**
   * Get unread message count for the current user
   * @returns {Promise} Response with unread_count
   */
  getUnreadCount: () => {
    return apiClient.get('/order-communications/communication-threads/', {
      params: {
        has_unread: true,
        page_size: 1000 // Get all to count accurately
      }
    }).then(response => {
      // Count total unread messages across all threads
      const unreadCount = response.data.results?.reduce((total, thread) => {
        return total + (thread.unread_count || 0)
      }, 0) || 0
      
      return {
        data: {
          unread_count: unreadCount,
          unread_threads: response.data.results?.length || 0
        }
      }
    })
  },

  /**
   * Get list of threads with unread messages
   * @param {Object} params - Query parameters
   * @returns {Promise} Response with threads
   */
  getUnreadThreads: (params = {}) => {
    return communications.listThreads({
      ...params,
      has_unread: true
    })
  },

  /**
   * Get all threads for the current user
   * @param {Object} params - Query parameters
   * @returns {Promise} Response with threads
   */
  getThreads: (params = {}) => {
    return communications.listThreads(params)
  },

  /**
   * Get a specific thread
   * @param {number} threadId - Thread ID
   * @returns {Promise} Response with thread data
   */
  getThread: (threadId) => {
    return communications.getThread(threadId)
  },

  /**
   * Get messages for a thread
   * @param {number} threadId - Thread ID
   * @param {Object} params - Query parameters
   * @returns {Promise} Response with messages
   */
  getMessages: (threadId, params = {}) => {
    return communications.listMessages(threadId, params)
  },

  /**
   * Send a message in a thread
   * @param {number} threadId - Thread ID
   * @param {Object} data - Message data
   * @returns {Promise} Response with created message
   */
  sendMessage: (threadId, data) => {
    return communications.sendMessage(threadId, data)
  },

  /**
   * Send a simple message (auto-detects recipient)
   * @param {number} threadId - Thread ID
   * @param {string} message - Message text
   * @param {File} attachment - Optional attachment
   * @param {number} replyTo - Optional message ID to reply to
   * @returns {Promise} Response with created message
   */
  sendMessageSimple: (threadId, message, attachment = null, replyTo = null) => {
    return communications.sendMessageSimple(threadId, message, attachment, replyTo)
  },

  /**
   * Mark a message as read
   * @param {number} threadId - Thread ID
   * @param {number} messageId - Message ID
   * @returns {Promise} Response
   */
  markMessageAsRead: (threadId, messageId) => {
    return communications.markMessageAsRead(threadId, messageId)
  },

  /**
   * Mark entire thread as read
   * @param {number} threadId - Thread ID
   * @returns {Promise} Response
   */
  markThreadAsRead: (threadId) => {
    return communications.markThreadAsRead(threadId)
  },

  /**
   * Start a thread for an order
   * @param {number} orderId - Order ID
   * @param {number} recipientId - Optional recipient ID
   * @returns {Promise} Response with thread data
   */
  startThreadForOrder: (orderId, recipientId = null) => {
    return communications.startThreadForOrder(orderId, recipientId)
  },

  /**
   * Create a general thread
   * @param {number} recipientId - Recipient user ID
   * @param {string} message - Initial message
   * @param {string} threadType - Thread type
   * @returns {Promise} Response with thread data
   */
  createGeneralThread: (recipientId, message, threadType = 'general') => {
    return communications.createGeneralThread(recipientId, message, threadType)
  },

  /**
   * Get typing status for a thread
   * @param {number} threadId - Thread ID
   * @returns {Promise} Response with typing status
   */
  getTypingStatus: (threadId) => {
    return communications.getTypingStatus(threadId)
  },

  /**
   * Set typing indicator for a thread
   * @param {number} threadId - Thread ID
   * @returns {Promise} Response
   */
  setTyping: (threadId) => {
    return communications.setTyping(threadId)
  },

  /**
   * Add reaction to a message
   * @param {number} threadId - Thread ID
   * @param {number} messageId - Message ID
   * @param {string} reaction - Reaction emoji
   * @returns {Promise} Response
   */
  addReaction: (threadId, messageId, reaction) => {
    return communications.addReaction(threadId, messageId, reaction)
  },

  /**
   * Remove reaction from a message
   * @param {number} threadId - Thread ID
   * @param {number} messageId - Message ID
   * @param {string} reaction - Reaction emoji
   * @returns {Promise} Response
   */
  removeReaction: (threadId, messageId, reaction) => {
    return communications.removeReaction(threadId, messageId, reaction)
  }
}
