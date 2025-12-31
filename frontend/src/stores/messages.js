/**
 * Messages Store
 * Centralized state management for messages to prevent duplicate API calls
 * and coordinate refreshes across components
 */

import { ref, reactive } from 'vue'
import { communicationsAPI } from '@/api'

// Shared cache for threads
const threadsCache = reactive({
  data: [],
  lastFetch: null,
  fetching: false,
  cacheTime: 30000 // Increased to 30 seconds cache for better performance
})

// Shared cache for messages by thread ID
const messagesCache = reactive({
  data: {},
  lastFetch: {},
  fetching: {},
  cacheTime: 15000 // Increased to 15 seconds cache
})

// Cache size limits to prevent memory issues
const MAX_CACHED_THREADS = 200
const MAX_CACHED_MESSAGES_PER_THREAD = 100

// Active refresh intervals (to prevent multiple intervals)
const activeIntervals = new Set()

// SSE realtime state
const realtimeStatus = ref('idle')
const lastRealtimeEventAt = ref(null)
const realtimeRetryCount = ref(0)
let realtimeSource = null
let realtimeReconnectTimer = null

const cleanupRealtime = () => {
  if (realtimeSource) {
    realtimeSource.close()
    realtimeSource = null
  }
  if (realtimeReconnectTimer) {
    clearTimeout(realtimeReconnectTimer)
    realtimeReconnectTimer = null
  }
}

const scheduleRealtimeReconnect = () => {
  if (realtimeReconnectTimer) return
  const baseDelay = 2000
  const delay = Math.min(30000, baseDelay * Math.max(1, realtimeRetryCount.value + 1))
  realtimeReconnectTimer = setTimeout(() => {
    realtimeReconnectTimer = null
    realtimeRetryCount.value += 1
    connectRealtime()
  }, delay)
}

function connectRealtime() {
  if (realtimeSource) {
    return // Already connected
  }

  realtimeStatus.value = 'connecting'

  try {
    // EventSource can't send custom headers, so we pass the token as a query parameter
    const token = localStorage.getItem('access_token')
    
    // Don't connect if no token (will fail with 401)
    if (!token) {
      realtimeStatus.value = 'disconnected'
      return
    }
    
    // Check if token is expired (basic check - JWT tokens have exp claim)
    try {
      const tokenParts = token.split('.')
      if (tokenParts.length === 3) {
        const payload = JSON.parse(atob(tokenParts[1]))
        const exp = payload.exp * 1000 // Convert to milliseconds
        if (Date.now() >= exp) {
          // Token expired, don't connect
          realtimeStatus.value = 'disconnected'
          return
        }
      }
    } catch (e) {
      // If we can't parse token, try anyway
    }
    
    const url = `/api/v1/order-communications/communication-threads-stream/?token=${encodeURIComponent(token)}`
    
    realtimeSource = new EventSource(url)

    realtimeSource.addEventListener('threads_update', (event) => {
      try {
        const payload = JSON.parse(event.data || '[]')
        threadsCache.data = Array.isArray(payload) ? payload : []
        threadsCache.lastFetch = Date.now()
        realtimeStatus.value = 'connected'
        realtimeRetryCount.value = 0
        lastRealtimeEventAt.value = new Date()
      } catch (error) {
        // Silently handle parse errors - don't spam console
        if (import.meta.env.DEV) {
          console.error('Failed to parse threads_update payload', error)
        }
      }
    })

    realtimeSource.onopen = () => {
      realtimeStatus.value = 'connected'
      realtimeRetryCount.value = 0
    }

    realtimeSource.onerror = (error) => {
      // Don't log 401 errors - they're expected when token expires
      const isAuthError = realtimeSource?.readyState === EventSource.CLOSED
      if (!isAuthError && import.meta.env.DEV) {
        console.debug('SSE connection error (non-critical)', error)
      }
      realtimeStatus.value = 'disconnected'
      cleanupRealtime()
      // Only reconnect if we have a valid token
      const currentToken = localStorage.getItem('access_token')
      if (currentToken) {
        scheduleRealtimeReconnect()
      }
    }
  } catch (error) {
    // Silently handle connection errors - don't spam console
    if (import.meta.env.DEV) {
      console.error('Failed to open communications SSE stream', error)
    }
    realtimeStatus.value = 'disconnected'
    cleanupRealtime()
    // Only reconnect if we have a valid token
    const currentToken = localStorage.getItem('access_token')
    if (currentToken) {
      scheduleRealtimeReconnect()
    }
  }
}

function disconnectRealtime() {
  cleanupRealtime()
  realtimeStatus.value = 'idle'
}

/**
 * Get threads with caching and deduplication
 */
export async function getThreads(forceRefresh = false) {
  const now = Date.now()
  
  // Return cached data if still valid and not forcing refresh
  if (!forceRefresh && threadsCache.data.length > 0 && threadsCache.lastFetch) {
    const cacheAge = now - threadsCache.lastFetch
    if (cacheAge < threadsCache.cacheTime && !threadsCache.fetching) {
      return threadsCache.data
    }
  }
  
  // Prevent duplicate requests
  if (threadsCache.fetching) {
    // Wait for ongoing request
    return new Promise((resolve) => {
      const checkInterval = setInterval(() => {
        if (!threadsCache.fetching && threadsCache.lastFetch) {
          clearInterval(checkInterval)
          resolve(threadsCache.data)
        }
      }, 100)
    })
  }
  
  threadsCache.fetching = true
  
  try {
    const response = await communicationsAPI.listThreads({
      page_size: 100 // Limit initial load
    })
    const threads = response.data.results || response.data || []
    
    // Limit cached threads to prevent memory issues
    const limitedThreads = threads.slice(0, MAX_CACHED_THREADS)
    
    threadsCache.data = limitedThreads
    threadsCache.lastFetch = now
    
    return limitedThreads
  } catch (error) {
    // Handle rate limiting (429) gracefully
    if (error.response?.status === 429) {
      // Return cached data if available, otherwise empty array
      if (threadsCache.data.length > 0) {
        return threadsCache.data
      }
      return []
    }
    
    // Only log non-rate-limit errors in dev mode
    if (import.meta.env.DEV && error.response?.status !== 429) {
      console.error('Failed to load threads:', error)
    }
    
    // Return cached data on error if available
    if (threadsCache.data.length > 0) {
      return threadsCache.data
    }
    
    // Don't throw for expected errors (404, 403, 429)
    if (error.response?.status === 404 || error.response?.status === 403 || error.response?.status === 429) {
      return []
    }
    
    throw error
  } finally {
    threadsCache.fetching = false
  }
}

/**
 * Get messages for a thread with caching
 */
export async function getThreadMessages(threadId, forceRefresh = false) {
  const now = Date.now()
  
  // Return cached data if still valid
  if (!forceRefresh && messagesCache.data[threadId] && messagesCache.lastFetch[threadId]) {
    const cacheAge = now - messagesCache.lastFetch[threadId]
    if (cacheAge < messagesCache.cacheTime && !messagesCache.fetching[threadId]) {
      return messagesCache.data[threadId]
    }
  }
  
  // Prevent duplicate requests
  if (messagesCache.fetching[threadId]) {
    return new Promise((resolve) => {
      const checkInterval = setInterval(() => {
        if (!messagesCache.fetching[threadId] && messagesCache.lastFetch[threadId]) {
          clearInterval(checkInterval)
          resolve(messagesCache.data[threadId] || [])
        }
      }, 100)
    })
  }
  
  messagesCache.fetching[threadId] = true
  
  try {
    const response = await communicationsAPI.listMessages(threadId, {
      page_size: MAX_CACHED_MESSAGES_PER_THREAD
    })
    const messages = (response.data.results || response.data || []).reverse()
    
    // Limit cached messages to prevent memory issues
    const limitedMessages = messages.slice(0, MAX_CACHED_MESSAGES_PER_THREAD)
    
    messagesCache.data[threadId] = limitedMessages
    messagesCache.lastFetch[threadId] = now
    
    return limitedMessages
  } catch (error) {
    console.error('Failed to load messages:', error)
    // Return cached data on error if available
    if (messagesCache.data[threadId]) {
      return messagesCache.data[threadId]
    }
    throw error
  } finally {
    messagesCache.fetching[threadId] = false
  }
}

/**
 * Invalidate cache for threads
 */
export function invalidateThreadsCache() {
  threadsCache.lastFetch = null
}

/**
 * Invalidate cache for a specific thread's messages
 */
export function invalidateThreadMessagesCache(threadId) {
  if (threadId) {
    delete messagesCache.data[threadId]
    delete messagesCache.lastFetch[threadId]
  } else {
    // Invalidate all
    messagesCache.data = {}
    messagesCache.lastFetch = {}
  }
}

/**
 * Start a shared refresh interval (only one active at a time)
 */
export function startSharedRefresh(callback, interval = 30000) {
  // Clear any existing intervals
  stopAllRefreshes()
  
  const intervalId = setInterval(() => {
    callback()
  }, interval)
  
  activeIntervals.add(intervalId)
  
  return intervalId
}

/**
 * Stop all refresh intervals
 */
export function stopAllRefreshes() {
  activeIntervals.forEach(intervalId => {
    clearInterval(intervalId)
  })
  activeIntervals.clear()
}

/**
 * Stop a specific refresh interval
 */
export function stopRefresh(intervalId) {
  if (intervalId) {
    clearInterval(intervalId)
    activeIntervals.delete(intervalId)
  }
}

export default {
  getThreads,
  getThreadMessages,
  invalidateThreadsCache,
  invalidateThreadMessagesCache,
  startSharedRefresh,
  stopAllRefreshes,
  stopRefresh,
  connectRealtime,
  disconnectRealtime,
  realtimeStatus,
  lastRealtimeEventAt,
}

