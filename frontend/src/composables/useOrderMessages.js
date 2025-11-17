/**
 * Composable for Order Messages
 * Handles order message loading with rate limiting and error handling
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { listThreads, startThreadForOrder, getThreadMessages, sendMessage, markThreadAsRead, clearThreadsCache } from '@/api/communications'
import { throttle } from '@/utils/messageUtils'

export function useOrderMessages(orderId) {
  const threads = ref([])
  const messages = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref(null)
  const creatingThread = ref(false)
  
  const authStore = useAuthStore()
  
  // Throttle API calls to prevent 429 errors
  const loadThreads = throttle(async () => {
    if (!orderId || !authStore.token) {
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await listThreads(orderId)
      
      threads.value = response.data.results || response.data || []
      
      // Calculate total unread count
      unreadCount.value = threads.value.reduce((sum, thread) => {
        return sum + (thread.unread_count || 0)
      }, 0)
    } catch (err) {
      if (err.message.includes('Authentication')) {
        error.value = 'Authentication required. Please log in again.'
      } else if (err.message.includes('permission')) {
        error.value = 'You do not have permission to view these messages.'
      } else if (err.message.includes('Too many requests')) {
        error.value = 'Too many requests. Please wait a moment.'
        // Retry after a delay
        setTimeout(() => loadThreads(), 5000)
      } else {
        error.value = err.message || 'Failed to load threads'
        console.error('Failed to load threads:', err)
      }
    } finally {
      loading.value = false
    }
  }, 5000) // Throttle to max once per 5 seconds (matches cache time)
  
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
        
        // Clear cache and reload to get fresh data
        clearThreadsCache()
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
  
  const loadMessages = throttle(async (threadId) => {
    if (!threadId || !authStore.token) {
      return
    }
    
    try {
      const response = await getThreadMessages(threadId)
      messages.value = response.data.results || response.data || []
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
  }, 3000) // Throttle to max once per 3 seconds
  
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
   * Send a message in a thread
   */
  const sendThreadMessage = async (threadId, messageText, options = {}) => {
    if (!threadId || !messageText || !authStore.token) {
      throw new Error('Thread ID, message, and authentication required')
    }
    
    try {
      const response = await sendMessage(threadId, messageText, options)
      
      // Reload messages to show the new one
      await loadMessages(threadId)
      
      // Clear cache and reload threads to update unread counts
      clearThreadsCache()
      await loadThreads()
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to send message'
      console.error('Failed to send message:', err)
      throw err
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
  
  // Auto-refresh with longer intervals to prevent rate limiting
  let refreshInterval = null
  
  const startAutoRefresh = () => {
    // Refresh every 30 seconds instead of constantly
    refreshInterval = setInterval(() => {
      loadThreads()
    }, 30000)
  }
  
  const stopAutoRefresh = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
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

