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
  cacheTime: 10000 // 10 seconds cache
})

// Shared cache for messages by thread ID
const messagesCache = reactive({
  data: {},
  lastFetch: {},
  fetching: {},
  cacheTime: 5000 // 5 seconds cache
})

// Active refresh intervals (to prevent multiple intervals)
const activeIntervals = new Set()

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
    const response = await communicationsAPI.listThreads({})
    const threads = response.data.results || response.data || []
    
    threadsCache.data = threads
    threadsCache.lastFetch = now
    
    return threads
  } catch (error) {
    console.error('Failed to load threads:', error)
    // Return cached data on error if available
    if (threadsCache.data.length > 0) {
      return threadsCache.data
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
    const response = await communicationsAPI.listMessages(threadId)
    const messages = (response.data.results || response.data || []).reverse()
    
    messagesCache.data[threadId] = messages
    messagesCache.lastFetch[threadId] = now
    
    return messages
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
  stopRefresh
}

