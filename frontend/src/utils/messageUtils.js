/**
 * Message Utilities
 * Helper functions for handling order messages and unread counts
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Rate limiting: prevent too many requests
let lastUnreadCountRequest = 0
let lastUnreadCountValue = 0
const UNREAD_COUNT_CACHE_TIME = 5000 // 5 seconds

/**
 * Load unread message count for an order
 * @param {number} orderId - Order ID
 * @returns {Promise<number>} Unread message count
 */
export async function loadUnreadMessageCount(orderId) {
  try {
    const authStore = useAuthStore()
    
    // Rate limiting: don't request more than once every 5 seconds
    const now = Date.now()
    if (now - lastUnreadCountRequest < UNREAD_COUNT_CACHE_TIME) {
      return lastUnreadCountValue
    }
    
    if (!authStore.token) {
      // Silently return 0 if no auth token (expected when not logged in)
      return 0
    }
    
    const response = await axios.get(`/api/v1/order-communications/threads/?order=${orderId}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    // Calculate total unread count from threads
    const threads = response.data.results || response.data || []
    const totalUnread = threads.reduce((sum, thread) => {
      return sum + (thread.unread_count || 0)
    }, 0)
    
    lastUnreadCountRequest = now
    lastUnreadCountValue = totalUnread
    
    return totalUnread
  } catch (error) {
    // Handle errors gracefully
    if (error.response?.status === 401) {
      console.warn('Unauthorized: Token may have expired')
      // Try to refresh token or redirect to login
      return 0
    }
    if (error.response?.status === 429) {
      console.warn('Rate limited: Too many requests')
      // Return cached value if available
      return lastUnreadCountValue
    }
    console.error('Failed to load unread message count:', error)
    return 0
  }
}

/**
 * Load unread notification count
 * @returns {Promise<number>} Unread notification count
 */
export async function loadUnreadNotificationCount() {
  try {
    const authStore = useAuthStore()
    
    // Rate limiting
    const now = Date.now()
    if (now - lastUnreadCountRequest < UNREAD_COUNT_CACHE_TIME) {
      return lastUnreadCountValue
    }
    
    if (!authStore.token) {
      return 0
    }
    
    const response = await axios.get('/api/v1/notifications_system/unread-count/', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    const count = response.data.unread_count || 0
    lastUnreadCountRequest = now
    lastUnreadCountValue = count
    
    return count
  } catch (error) {
    if (error.response?.status === 401) {
      console.warn('Unauthorized: Token may have expired')
      return 0
    }
    if (error.response?.status === 429) {
      console.warn('Rate limited: Too many requests')
      return lastUnreadCountValue
    }
    console.error('Failed to load unread count:', error)
    return 0
  }
}

/**
 * Debounce function to limit API calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function to limit API calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

