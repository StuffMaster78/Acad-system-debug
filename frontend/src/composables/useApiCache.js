import { ref } from 'vue'

/**
 * API Response Caching Composable
 * Provides caching for API responses to reduce redundant requests
 * 
 * @param {number} defaultTTL - Default cache TTL in milliseconds (default: 5 minutes)
 * @returns {Object} Cache utilities
 */
export function useApiCache(defaultTTL = 5 * 60 * 1000) {
  const cache = ref(new Map())
  
  /**
   * Generate cache key from URL and params
   */
  const getCacheKey = (url, params = {}) => {
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&')
    return `${url}?${sortedParams}`
  }
  
  /**
   * Get cached response if available and not expired
   */
  const get = (url, params = {}) => {
    const key = getCacheKey(url, params)
    const cached = cache.value.get(key)
    
    if (!cached) return null
    
    const now = Date.now()
    if (now > cached.expiresAt) {
      cache.value.delete(key)
      return null
    }
    
    return cached.data
  }
  
  /**
   * Set cache entry
   */
  const set = (url, params = {}, data, ttl = defaultTTL) => {
    const key = getCacheKey(url, params)
    const expiresAt = Date.now() + ttl
    
    cache.value.set(key, {
      data,
      expiresAt,
      cachedAt: Date.now()
    })
  }
  
  /**
   * Invalidate cache by URL pattern
   */
  const invalidate = (urlPattern) => {
    const keysToDelete = []
    for (const key of cache.value.keys()) {
      if (key.includes(urlPattern)) {
        keysToDelete.push(key)
      }
    }
    keysToDelete.forEach(key => cache.value.delete(key))
  }
  
  /**
   * Clear all cache
   */
  const clear = () => {
    cache.value.clear()
  }
  
  /**
   * Clear expired entries
   */
  const clearExpired = () => {
    const now = Date.now()
    const keysToDelete = []
    
    for (const [key, value] of cache.value.entries()) {
      if (now > value.expiresAt) {
        keysToDelete.push(key)
      }
    }
    
    keysToDelete.forEach(key => cache.value.delete(key))
  }
  
  /**
   * Get cache stats
   */
  const getStats = () => {
    const now = Date.now()
    let total = 0
    let expired = 0
    
    for (const value of cache.value.values()) {
      total++
      if (now > value.expiresAt) {
        expired++
      }
    }
    
    return {
      total,
      expired,
      active: total - expired
    }
  }
  
  // Auto-cleanup expired entries every 5 minutes
  if (typeof window !== 'undefined') {
    setInterval(clearExpired, 5 * 60 * 1000)
  }
  
  return {
    get,
    set,
    invalidate,
    clear,
    clearExpired,
    getStats
  }
}

