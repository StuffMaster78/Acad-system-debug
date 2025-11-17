/**
 * Communications API Service
 * Handles order messages, threads, and communication with rate limiting
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Rate limiting: prevent too many requests
let lastListThreadsRequest = 0
let cachedThreads = null
const THREADS_CACHE_TIME = 5000 // 5 seconds

// Create axios instance with interceptors
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// Handle rate limiting in response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 5
      console.warn(`Rate limited. Retry after ${retryAfter} seconds`)
      
      // Return cached data if available
      if (cachedThreads) {
        return { data: cachedThreads, fromCache: true }
      }
      
      // Wait and retry once
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000))
      return apiClient.request(error.config)
    }
    return Promise.reject(error)
  }
)

/**
 * List communication threads for an order
 * @param {number} orderId - Order ID
 * @param {Object} options - Additional options
 * @returns {Promise} Threads response
 */
export async function listThreads(orderId, options = {}) {
  try {
    const authStore = useAuthStore()
    
    if (!authStore.token) {
      throw new Error('Authentication required')
    }
    
    // Rate limiting: don't request more than once every 5 seconds
    const now = Date.now()
    if (now - lastListThreadsRequest < THREADS_CACHE_TIME && cachedThreads) {
      return { data: cachedThreads, fromCache: true }
    }
    
    const response = await apiClient.get('/order-communications/communication-threads/', {
      params: {
        order: orderId,
        ...options
      }
    })
    
    // Cache the response
    lastListThreadsRequest = now
    cachedThreads = response.data
    
    return response
  } catch (error) {
    if (error.response?.status === 429) {
      // Return cached data if available
      if (cachedThreads) {
        console.warn('Rate limited, returning cached threads')
        return { data: cachedThreads, fromCache: true }
      }
      throw new Error('Too many requests. Please wait a moment and try again.')
    }
    if (error.response?.status === 401) {
      throw new Error('Authentication required. Please log in again.')
    }
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to view these threads.')
    }
    throw error
  }
}

/**
 * Start a conversation thread for an order
 * Uses the simplified endpoint that automatically sets up participants
 * @param {number} orderId - Order ID
 * @returns {Promise} Created thread response
 */
export async function startThreadForOrder(orderId) {
  try {
    const authStore = useAuthStore()
    
    if (!authStore.token) {
      throw new Error('Authentication required')
    }
    
    if (!orderId) {
      throw new Error('Order ID is required')
    }
    
    // Use the simplified endpoint that doesn't require recipients
    const response = await apiClient.post('/order-communications/communication-threads/start-for-order/', {
      order_id: orderId
    })
    
    // Clear cache so next listThreads call gets fresh data
    cachedThreads = null
    lastListThreadsRequest = 0
    
    // The endpoint returns either:
    // - { detail: "...", thread: {...} } for new thread
    // - { detail: "...", thread: {...} } for existing thread
    return response
  } catch (error) {
    // Handle specific error cases
    if (error.response?.status === 400) {
      const detail = error.response.data?.detail || 'Invalid request. Please check the order ID.'
      throw new Error(detail)
    }
    if (error.response?.status === 401) {
      throw new Error('Authentication required. Please log in again.')
    }
    if (error.response?.status === 403) {
      const detail = error.response.data?.detail || 'You do not have permission to start a conversation for this order.'
      throw new Error(detail)
    }
    if (error.response?.status === 404) {
      throw new Error('Order not found.')
    }
    if (error.response?.status === 429) {
      throw new Error('Too many requests. Please wait a moment and try again.')
    }
    if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.')
    }
    
    // If it's already an Error object, re-throw it
    if (error instanceof Error) {
      throw error
    }
    
    // Otherwise, create a generic error
    throw new Error(error.message || 'Failed to start conversation')
  }
}

/**
 * Get messages for a thread
 * @param {number} threadId - Thread ID
 * @param {Object} options - Pagination options
 * @returns {Promise} Messages response
 */
export async function getThreadMessages(threadId, options = {}) {
  try {
    const authStore = useAuthStore()
    
    if (!authStore.token) {
      throw new Error('Authentication required')
    }
    
    const response = await apiClient.get(`/order-communications/communication-threads/${threadId}/messages/`, {
      params: options
    })
    
    return response
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Authentication required.')
    }
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to view these messages.')
    }
    if (error.response?.status === 429) {
      throw new Error('Too many requests. Please wait a moment.')
    }
    throw error
  }
}

/**
 * Send a message in a thread
 * @param {number} threadId - Thread ID
 * @param {string} message - Message text
 * @param {Object} options - Additional options (attachment, etc.)
 * @returns {Promise} Created message response
 */
export async function sendMessage(threadId, message, options = {}) {
  try {
    const authStore = useAuthStore()
    
    if (!authStore.token) {
      throw new Error('Authentication required')
    }
    
    const formData = new FormData()
    formData.append('message', message)
    
    if (options.attachment) {
      formData.append('attachment', options.attachment)
    }
    
    if (options.message_type) {
      formData.append('message_type', options.message_type)
    }
    
    const response = await apiClient.post(
      `/order-communications/communication-threads/${threadId}/messages/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    // Clear cache so next listThreads call gets fresh data
    cachedThreads = null
    lastListThreadsRequest = 0
    
    return response
  } catch (error) {
    if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || 'Invalid message. Please check your input.')
    }
    if (error.response?.status === 401) {
      throw new Error('Authentication required.')
    }
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to send messages in this thread.')
    }
    if (error.response?.status === 429) {
      throw new Error('Too many requests. Please wait a moment.')
    }
    throw error
  }
}

/**
 * Mark messages as read
 * @param {number} threadId - Thread ID
 * @returns {Promise} Success response
 */
export async function markThreadAsRead(threadId) {
  try {
    const authStore = useAuthStore()
    
    if (!authStore.token) {
      throw new Error('Authentication required')
    }
    
    const response = await apiClient.post(
      `/order-communications/communication-threads/${threadId}/mark-as-read/`
    )
    
    // Clear cache
    cachedThreads = null
    lastListThreadsRequest = 0
    
    return response
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Authentication required.')
    }
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to mark this thread as read.')
    }
    throw error
  }
}

/**
 * Clear the threads cache (useful after creating/updating threads)
 */
export function clearThreadsCache() {
  cachedThreads = null
  lastListThreadsRequest = 0
}

export default {
  listThreads,
  startThreadForOrder,
  getThreadMessages,
  sendMessage,
  markThreadAsRead,
  clearThreadsCache
}

