/**
 * Order caching utility for offline access
 * Stores orders in localStorage with expiration and fallback support
 */

const CACHE_PREFIX = 'order_cache_'
const CACHE_EXPIRY_PREFIX = 'order_cache_expiry_'
const CACHE_VERSION = '1.0'
const DEFAULT_CACHE_TTL = 24 * 60 * 60 * 1000 // 24 hours in milliseconds
const MAX_CACHE_SIZE = 10 * 1024 * 1024 // 10MB max cache size

/**
 * Get cache key for order list
 */
function getListCacheKey(params = {}) {
  // Create a stable key from params
  const keyParts = Object.keys(params)
    .sort()
    .map(k => `${k}:${params[k]}`)
    .join('|')
  return `${CACHE_PREFIX}list_${keyParts || 'default'}`
}

/**
 * Get cache key for individual order
 */
function getOrderCacheKey(orderId) {
  return `${CACHE_PREFIX}order_${orderId}`
}

/**
 * Get expiry key for cache entry
 */
function getExpiryKey(cacheKey) {
  return cacheKey.replace(CACHE_PREFIX, CACHE_EXPIRY_PREFIX)
}

/**
 * Check if cache entry is expired
 */
function isExpired(cacheKey) {
  const expiryKey = getExpiryKey(cacheKey)
  const expiryStr = localStorage.getItem(expiryKey)
  if (!expiryStr) return true
  
  const expiry = parseInt(expiryStr, 10)
  return Date.now() > expiry
}

/**
 * Get cache entry
 */
function getCache(cacheKey) {
  try {
    if (isExpired(cacheKey)) {
      // Clean up expired entry
      removeCache(cacheKey)
      return null
    }
    
    const data = localStorage.getItem(cacheKey)
    if (!data) return null
    
    const parsed = JSON.parse(data)
    return parsed
  } catch (error) {
    console.error('Error reading from cache:', error)
    return null
  }
}

/**
 * Set cache entry
 */
function setCache(cacheKey, data, ttl = DEFAULT_CACHE_TTL) {
  try {
    // Check cache size before adding
    const dataStr = JSON.stringify(data)
    const size = new Blob([dataStr]).size
    
    // If adding this would exceed max size, clean up old entries
    if (size > MAX_CACHE_SIZE) {
      console.warn('Cache entry too large, skipping cache')
      return false
    }
    
    // Clean up expired entries periodically
    if (Math.random() < 0.1) { // 10% chance to clean up
      cleanupExpired()
    }
    
    const expiry = Date.now() + ttl
    localStorage.setItem(cacheKey, dataStr)
    localStorage.setItem(getExpiryKey(cacheKey), expiry.toString())
    
    return true
  } catch (error) {
    // Handle quota exceeded error
    if (error.name === 'QuotaExceededError') {
      console.warn('localStorage quota exceeded, cleaning up old entries')
      cleanupExpired()
      // Try once more after cleanup
      try {
        const dataStr = JSON.stringify(data)
        localStorage.setItem(cacheKey, dataStr)
        localStorage.setItem(getExpiryKey(cacheKey), (Date.now() + ttl).toString())
        return true
      } catch (retryError) {
        console.error('Failed to cache after cleanup:', retryError)
        return false
      }
    }
    console.error('Error writing to cache:', error)
    return false
  }
}

/**
 * Remove cache entry
 */
function removeCache(cacheKey) {
  try {
    localStorage.removeItem(cacheKey)
    localStorage.removeItem(getExpiryKey(cacheKey))
  } catch (error) {
    console.error('Error removing cache:', error)
  }
}

/**
 * Clean up expired cache entries
 */
function cleanupExpired() {
  try {
    const keys = Object.keys(localStorage)
    const now = Date.now()
    let cleaned = 0
    
    keys.forEach(key => {
      if (key.startsWith(CACHE_EXPIRY_PREFIX)) {
        const expiry = parseInt(localStorage.getItem(key), 10)
        if (expiry && now > expiry) {
          const cacheKey = key.replace(CACHE_EXPIRY_PREFIX, CACHE_PREFIX)
          removeCache(cacheKey)
          cleaned++
        }
      }
    })
    
    if (cleaned > 0) {
      console.log(`Cleaned up ${cleaned} expired cache entries`)
    }
  } catch (error) {
    console.error('Error cleaning up cache:', error)
  }
}

/**
 * Get cached order list
 */
export function getCachedOrderList(params = {}) {
  const cacheKey = getListCacheKey(params)
  const cached = getCache(cacheKey)
  
  if (cached) {
    return {
      data: cached,
      fromCache: true,
      timestamp: cached._cached_at || null
    }
  }
  
  return null
}

/**
 * Cache order list
 */
export function cacheOrderList(params = {}, data, ttl = DEFAULT_CACHE_TTL) {
  const cacheKey = getListCacheKey(params)
  const dataWithTimestamp = {
    ...data,
    _cached_at: Date.now(),
    _cache_version: CACHE_VERSION
  }
  setCache(cacheKey, dataWithTimestamp, ttl)
}

/**
 * Get cached order by ID
 */
export function getCachedOrder(orderId) {
  const cacheKey = getOrderCacheKey(orderId)
  const cached = getCache(cacheKey)
  
  if (cached) {
    return {
      data: cached,
      fromCache: true,
      timestamp: cached._cached_at || null
    }
  }
  
  return null
}

/**
 * Cache individual order
 */
export function cacheOrder(orderId, orderData, ttl = DEFAULT_CACHE_TTL) {
  const cacheKey = getOrderCacheKey(orderId)
  const dataWithTimestamp = {
    ...orderData,
    _cached_at: Date.now(),
    _cache_version: CACHE_VERSION
  }
  setCache(cacheKey, dataWithTimestamp, ttl)
}

/**
 * Invalidate order cache (remove from cache)
 */
export function invalidateOrderCache(orderId) {
  const cacheKey = getOrderCacheKey(orderId)
  removeCache(cacheKey)
}

/**
 * Invalidate all order list caches
 */
export function invalidateAllListCaches() {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(CACHE_PREFIX) && key.includes('list_')) {
        removeCache(key)
      }
    })
  } catch (error) {
    console.error('Error invalidating list caches:', error)
  }
}

/**
 * Clear all order caches
 */
export function clearAllOrderCaches() {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(CACHE_PREFIX) || key.startsWith(CACHE_EXPIRY_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
    console.log('All order caches cleared')
  } catch (error) {
    console.error('Error clearing caches:', error)
  }
}

/**
 * Get cache statistics
 */
export function getCacheStats() {
  try {
    const keys = Object.keys(localStorage)
    const orderKeys = keys.filter(k => k.startsWith(CACHE_PREFIX))
    const expiredKeys = keys.filter(k => {
      if (k.startsWith(CACHE_EXPIRY_PREFIX)) {
        const expiry = parseInt(localStorage.getItem(k), 10)
        return expiry && Date.now() > expiry
      }
      return false
    })
    
    let totalSize = 0
    orderKeys.forEach(key => {
      const data = localStorage.getItem(key)
      if (data) {
        totalSize += new Blob([data]).size
      }
    })
    
    return {
      totalEntries: orderKeys.length,
      expiredEntries: expiredKeys.length,
      totalSize: totalSize,
      totalSizeMB: (totalSize / (1024 * 1024)).toFixed(2)
    }
  } catch (error) {
    console.error('Error getting cache stats:', error)
    return null
  }
}

/**
 * Enhanced API call with cache fallback
 */
export async function cachedApiCall(apiCall, cacheKey, cacheFn, options = {}) {
  const {
    useCache = true,
    cacheOnError = true,
    ttl = DEFAULT_CACHE_TTL,
    onCacheHit = null,
    onCacheMiss = null
  } = options
  
  // Try to get from cache first if enabled
  if (useCache) {
    const cached = cacheKey ? getCache(cacheKey) : null
    if (cached && !isExpired(cacheKey)) {
      if (onCacheHit) onCacheHit(cached)
      return {
        data: cached,
        fromCache: true,
        cached: true
      }
    }
  }
  
  // Try API call
  try {
    const response = await apiCall()
    const data = response.data || response
    
    // Cache successful response
    if (useCache && cacheFn) {
      cacheFn(data, ttl)
    }
    
    if (onCacheMiss) onCacheMiss(data)
    
    return {
      data,
      fromCache: false,
      cached: false
    }
  } catch (error) {
    // On error, try to return cached data if available
    if (cacheOnError && useCache) {
      const cached = cacheKey ? getCache(cacheKey) : null
      if (cached) {
        console.warn('API call failed, returning cached data:', error)
        return {
          data: cached,
          fromCache: true,
          cached: true,
          error: error
        }
      }
    }
    
    // Re-throw error if no cache available
    throw error
  }
}

// Clean up expired entries on module load
if (typeof window !== 'undefined') {
  cleanupExpired()
}

