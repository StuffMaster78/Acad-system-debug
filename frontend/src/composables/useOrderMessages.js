/**
 * Composable for Order Messages
 * Handles order message loading with rate limiting and error handling
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { startThreadForOrder, markThreadAsRead } from '@/api/communications'
import messagesStore from '@/stores/messages'

export function useOrderMessages(orderId) {
  const threads = ref([])
  const messages = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref(null)
  const creatingThread = ref(false)
  
  const authStore = useAuthStore()
  
  // Use shared cache to prevent duplicate requests
  const loadThreads = async () => {
    if (!orderId || !authStore.token) {
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      // Use shared cache store instead of direct API call
      const allThreads = await messagesStore.getThreads()
      
      // Filter threads for this order
      threads.value = allThreads.filter(thread => {
        const threadOrderId = thread.order || thread.order_id
        return threadOrderId && parseInt(threadOrderId) === parseInt(orderId)
      })
      
      // Calculate total unread count
      unreadCount.value = threads.value.reduce((sum, thread) => {
        return sum + (thread.unread_count || 0)
      }, 0)
    } catch (err) {
      // Handle rate limiting (429) gracefully
      if (err.response?.status === 429 || err.message.includes('Too many requests')) {
        error.value = 'Too many requests. Please wait a moment.'
        // Retry after a delay (only once)
        if (!threads.value.length) {
          setTimeout(() => loadThreads(), 5000)
        }
        return
      }
      
      // Handle auth errors
      if (err.response?.status === 401 || err.message.includes('Authentication')) {
        error.value = 'Authentication required. Please log in again.'
        return
      }
      
      // Handle permission errors
      if (err.response?.status === 403 || err.message.includes('permission')) {
        error.value = 'You do not have permission to view these messages.'
        return
      }
      
      // Handle 404 gracefully (endpoint might not exist)
      if (err.response?.status === 404) {
        threads.value = []
        return
      }
      
      // Only log unexpected errors in dev mode
      if (import.meta.env.DEV) {
        console.error('Failed to load threads:', err)
      }
      
      error.value = err.message || 'Failed to load threads'
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Start a new conversation thread for the order
   * Uses the simplified endpoint that automatically sets up participants
   */
  const createThread = async () => {
    if (!orderId) {
      throw new Error('Order ID is required')
    }
    
    if (!authStore.token) {
      throw new Error('Authentication required. Please log in.')
    }
    
    creatingThread.value = true
    error.value = null
    
    try {
      const response = await startThreadForOrder(orderId)
      
      // The endpoint returns { detail: "...", thread: {...} }
      const thread = response.data?.thread
      
      if (thread) {
        // Check if thread already exists in the list
        const existingIndex = threads.value.findIndex(t => t.id === thread.id)
        if (existingIndex >= 0) {
          // Update existing thread
          threads.value[existingIndex] = thread
        } else {
          // Add new thread to the list
          threads.value = [thread, ...threads.value]
        }
        
      // Invalidate cache and reload to get fresh data
      messagesStore.invalidateThreadsCache()
      await loadThreads()
        
        return thread
      } else {
        throw new Error('Thread was not returned from the server')
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to create thread'
      error.value = errorMessage
      console.error('Failed to create thread:', err)
      
      // If the error mentions "recipient", it might be using the wrong endpoint
      if (errorMessage.toLowerCase().includes('recipient')) {
        error.value = 'There was an issue starting the conversation. Please try again or contact support.'
        console.error('Possible issue: Using wrong endpoint or missing participants')
      }
      
      throw err
    } finally {
      creatingThread.value = false
    }
  }
  
  const loadMessages = async (threadId) => {
    if (!threadId || !authStore.token) {
      return
    }
    
    try {
      // Use shared cache store instead of direct API call
      messages.value = await messagesStore.getThreadMessages(threadId)
    } catch (err) {
      if (err.message.includes('Authentication')) {
        error.value = 'Authentication required.'
      } else if (err.message.includes('Too many requests')) {
        error.value = 'Too many requests. Please wait.'
        setTimeout(() => loadMessages(threadId), 5000)
      } else {
        error.value = err.message || 'Failed to load messages'
        console.error('Failed to load messages:', err)
      }
    }
  }
  
  const loadFiles = throttle(async () => {
    if (!orderId || !authStore.token) {
      return []
    }
    
    try {
      const axios = (await import('axios')).default
      
      const response = await axios.get(`/api/v1/order-files/files/?order=${orderId}`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      })
      
      return response.data.results || response.data || []
    } catch (err) {
      if (err.response?.status === 403) {
        console.warn('No permission to view files for this order')
        return []
      } else if (err.response?.status === 429) {
        console.warn('Rate limited: Too many file requests')
        return []
      } else {
        console.error('Failed to load files:', err)
        return []
      }
    }
  }, 5000) // Files can be throttled more
  
  /**
   * Send a message in a thread (simplified - auto-detects recipient)
   */
  const sendThreadMessage = async (threadId, messageText, options = {}) => {
    if (!threadId || !authStore.token) {
      throw new Error('Thread ID and authentication required')
    }
    
    if (!messageText && !options.attachment) {
      throw new Error('Message text or attachment is required')
    }
    
    try {
      // Use simplified endpoint that auto-detects recipient
      const commsAPI = await import('@/api/communications')
      const response = await commsAPI.default.sendMessageSimple(
        threadId,
        messageText || '',
        options.attachment || null,
        options.reply_to || null
      )
      
      // Reload messages to show the new one
      await loadMessages(threadId)
      
      // Invalidate cache and reload threads to update unread counts
      messagesStore.invalidateThreadsCache()
      messagesStore.invalidateThreadMessagesCache(threadId)
      await loadThreads()
      
      return response.data
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 
                      err.response?.data?.error || 
                      err.message || 
                      'Failed to send message. Please try again.'
      error.value = errorMsg
      console.error('Failed to send message:', err)
      throw new Error(errorMsg)
    }
  }
  
  /**
   * Mark thread as read
   */
  const markAsRead = async (threadId) => {
    try {
      await markThreadAsRead(threadId)
      // Reload threads to update unread count
      await loadThreads()
    } catch (err) {
      console.error('Failed to mark thread as read:', err)
    }
  }
  
  // Use shared refresh to prevent multiple intervals
  let refreshInterval = null
  
  const startAutoRefresh = () => {
    // Prefer SSE-based updates; this is a no-op if already connected.
    messagesStore.connectRealtime()
  }
  
  const stopAutoRefresh = () => {
    // Keep SSE connection shared across consumers; no-op here.
  }
  
  onMounted(() => {
    if (orderId) {
      loadThreads()
      startAutoRefresh()
    }
  })
  
  onUnmounted(() => {
    stopAutoRefresh()
  })
  
  return {
    threads,
    messages,
    unreadCount,
    loading,
    error,
    creatingThread,
    loadThreads,
    loadMessages,
    loadFiles,
    createThread,
    sendThreadMessage,
    markAsRead,
    startAutoRefresh,
    stopAutoRefresh
  }
}

