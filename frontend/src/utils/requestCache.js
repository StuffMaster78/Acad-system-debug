/**
 * Request Cache Utility
 * Simple in-memory cache for API requests
 */

const cache = new Map()
const DEFAULT_TTL = 5 * 60 * 1000 // 5 minutes

/**
 * Generate cache key from request config
 */
function getCacheKey(config) {
  const { url, params, method = 'GET' } = config
  if (method !== 'GET') return null // Only cache GET requests
  
  const sortedParams = params ? Object.keys(params)
    .sort()
    .map(key => `${key}=${JSON.stringify(params[key])}`)
    .join('&') : ''
  
  return `${method}:${url}${sortedParams ? `?${sortedParams}` : ''}`
}

/**
 * Get cached response
 */
export function getCachedResponse(config) {
  const key = getCacheKey(config)
  if (!key) return null
  
  const cached = cache.get(key)
  if (!cached) return null
  
  // Check if expired
  if (Date.now() > cached.expiresAt) {
    cache.delete(key)
    return null
  }
  
  return cached.data
}

/**
 * Cache response
 */
export function cacheResponse(config, data, ttl = DEFAULT_TTL) {
  const key = getCacheKey(config)
  if (!key) return
  
  cache.set(key, {
    data,
    expiresAt: Date.now() + ttl,
    cachedAt: Date.now()
  })
}

/**
 * Invalidate cache by URL pattern
 */
export function invalidateCache(pattern) {
  const keysToDelete = []
  for (const key of cache.keys()) {
    if (key.includes(pattern)) {
      keysToDelete.push(key)
    }
  }
  keysToDelete.forEach(key => cache.delete(key))
}

/**
 * Clear all cache
 */
export function clearCache() {
  cache.clear()
}

/**
 * Clear expired entries
 */
export function clearExpiredCache() {
  const now = Date.now()
  const keysToDelete = []
  
  for (const [key, value] of cache.entries()) {
    if (now > value.expiresAt) {
      keysToDelete.push(key)
    }
  }
  
  keysToDelete.forEach(key => cache.delete(key))
}

// Auto-cleanup expired entries every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(clearExpiredCache, 5 * 60 * 1000)
}

