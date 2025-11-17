/**
 * Session Management Composable
 * Handles session status checking and extension with rate limiting
 */

import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Rate limiting: prevent too many requests
let lastStatusRequest = 0
let lastExtendRequest = 0
let cachedStatus = null
let statusInterval = null

const STATUS_CACHE_TIME = 10000 // 10 seconds - status can be cached
const EXTEND_MIN_INTERVAL = 30000 // 30 seconds - extend only once per 30 seconds

/**
 * Get session status with rate limiting
 */
export async function getSessionStatus() {
  try {
    const authStore = useAuthStore()
    
    if (!authStore.accessToken) {
      return null
    }
    
    // Rate limiting: don't request more than once every 10 seconds
    const now = Date.now()
    if (now - lastStatusRequest < STATUS_CACHE_TIME && cachedStatus) {
      return cachedStatus
    }
    
    const response = await axios.get('/api/v1/auth/session-management/status/', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })
    
    // Cache the response
    lastStatusRequest = now
    cachedStatus = response.data
    
    return response.data
  } catch (error) {
    if (error.response?.status === 429) {
      // Return cached status if available
      if (cachedStatus) {
        console.warn('Rate limited, returning cached session status')
        return cachedStatus
      }
      return null
    }
    if (error.response?.status === 401) {
      // Session expired
      return null
    }
    console.error('Failed to get session status:', error)
    return null
  }
}

/**
 * Extend session with rate limiting
 */
export async function extendSession() {
  try {
    const authStore = useAuthStore()
    
    if (!authStore.accessToken) {
      return false
    }
    
    // Rate limiting: don't extend more than once every 30 seconds
    const now = Date.now()
    if (now - lastExtendRequest < EXTEND_MIN_INTERVAL) {
      console.warn('Session extend throttled - too soon since last extend')
      return false
    }
    
    const response = await axios.post('/api/v1/auth/session-management/extend/', {}, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })
    
    lastExtendRequest = now
    // Clear status cache to get fresh data
    cachedStatus = null
    lastStatusRequest = 0
    
    return response.data
  } catch (error) {
    if (error.response?.status === 429) {
      console.warn('Rate limited: Too many extend requests')
      return false
    }
    if (error.response?.status === 401) {
      // Session expired
      return false
    }
    console.error('Failed to extend session:', error)
    return false
  }
}

/**
 * Composable for session management
 * Automatically checks session status and extends when needed
 */
export function useSessionManagement(options = {}) {
  const {
    checkInterval = 60000, // Check every 60 seconds (1 minute)
    extendBeforeWarning = true, // Extend session before warning
    autoExtend = true // Automatically extend session
  } = options
  
  const sessionStatus = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  const authStore = useAuthStore()
  
  const checkSession = async () => {
    if (!authStore.isAuthenticated) {
      return
    }
    
    loading.value = true
    error.value = null
    
    try {
      const status = await getSessionStatus()
      if (status) {
        sessionStatus.value = status
        
        // Auto-extend if needed and enabled
        if (autoExtend && status.should_warn && status.remaining_seconds < status.warning_threshold) {
          // Extend session if it's getting close to timeout
          await extendSession()
          // Refresh status after extending
          const newStatus = await getSessionStatus()
          if (newStatus) {
            sessionStatus.value = newStatus
          }
        }
      }
    } catch (err) {
      error.value = err.message || 'Failed to check session status'
      console.error('Session check error:', err)
    } finally {
      loading.value = false
    }
  }
  
  const manualExtend = async () => {
    if (!authStore.isAuthenticated) {
      return false
    }
    
    loading.value = true
    try {
      const result = await extendSession()
      if (result) {
        // Refresh status after extending
        await checkSession()
        return true
      }
      return false
    } catch (err) {
      error.value = err.message || 'Failed to extend session'
      return false
    } finally {
      loading.value = false
    }
  }
  
  const startPolling = () => {
    // Initial check
    checkSession()
    
    // Set up interval with longer delay to prevent rate limiting
    statusInterval = setInterval(() => {
      checkSession()
    }, checkInterval)
  }
  
  const stopPolling = () => {
    if (statusInterval) {
      clearInterval(statusInterval)
      statusInterval = null
    }
  }
  
  onMounted(() => {
    if (authStore.isAuthenticated) {
      startPolling()
    }
  })
  
  onUnmounted(() => {
    stopPolling()
  })
  
  return {
    sessionStatus,
    loading,
    error,
    checkSession,
    extendSession: manualExtend,
    startPolling,
    stopPolling
  }
}

