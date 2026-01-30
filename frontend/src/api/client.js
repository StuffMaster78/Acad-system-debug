import axios from 'axios'
import { normalizeApiError, isAuthError } from '@/utils/error'
import { maskEndpoint, getUserRole } from '@/utils/endpoint-masker'
import { getCachedResponse, cacheResponse, invalidateCache } from '@/utils/requestCache'
import { deduplicateRequest } from '@/utils/requestDeduplication'

const apiBaseURL = import.meta.env.VITE_API_BASE_URL
  || import.meta.env.VITE_API_FULL_URL
  || (import.meta.env.DEV ? 'http://localhost:8000/api/v1' : '/api/v1')

const apiClient = axios.create({
  baseURL: apiBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Wrap axios methods to add request deduplication
const originalRequest = apiClient.request.bind(apiClient)
apiClient.request = function(config) {
  // Skip deduplication if flag is set
  if (config._skipDeduplication) {
    return originalRequest(config)
  }
  return deduplicateRequest(originalRequest, config)
}

// Wrap all HTTP methods
const methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
methods.forEach(method => {
  const originalMethod = apiClient[method].bind(apiClient)
  apiClient[method] = function(url, data, config = {}) {
    const fullConfig = { ...config, method, url, data }
    // Skip deduplication if flag is set
    if (fullConfig._skipDeduplication) {
      return originalMethod(url, data, config)
    }
    return deduplicateRequest(() => originalMethod(url, data, config), fullConfig)
  }
})

// Proactive token refresh - refresh token before it expires
let tokenRefreshInterval = null
let lastTokenRefresh = 0
const TOKEN_REFRESH_INTERVAL = 20 * 60 * 1000 // Refresh every 20 minutes (tokens last 1 day = 1440 min)
const TOKEN_REFRESH_COOLDOWN = 5 * 60 * 1000 // Don't refresh more than once per 5 minutes

function startProactiveTokenRefresh() {
  if (tokenRefreshInterval) {
    return // Already started
  }
  
  tokenRefreshInterval = setInterval(async () => {
    const now = Date.now()
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    
    // Don't refresh if no tokens or too soon since last refresh
    if (!accessToken || !refreshToken || (now - lastTokenRefresh < TOKEN_REFRESH_COOLDOWN)) {
      return
    }
    
    try {
      const baseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_FULL_URL || '/api/v1'
      const refreshURL = baseURL.endsWith('/api/v1') 
        ? `${baseURL}/auth/auth/refresh-token/`
        : `${baseURL}/api/v1/auth/auth/refresh-token/`
      
      const response = await axios.post(
        refreshURL,
        { refresh_token: refreshToken },
        {
          headers: {
            'Content-Type': 'application/json',
          }
        }
      )
      
      const { access_token } = response.data
      if (access_token) {
        localStorage.setItem('access_token', access_token)
        lastTokenRefresh = now
        console.debug('Token refreshed proactively')
      }
    } catch (error) {
      // Silently fail - token refresh will happen on next 401 anyway
      // Only log if it's not a rate limit (429) - those are expected
      if (error.response?.status !== 429) {
        console.debug('Proactive token refresh failed (non-critical):', error.message)
      }
    }
  }, TOKEN_REFRESH_INTERVAL)
}

function stopProactiveTokenRefresh() {
  if (tokenRefreshInterval) {
    clearInterval(tokenRefreshInterval)
    tokenRefreshInterval = null
  }
}

// Start proactive refresh when module loads (if tokens exist)
if (typeof window !== 'undefined') {
  if (localStorage.getItem('access_token') && localStorage.getItem('refresh_token')) {
    startProactiveTokenRefresh()
  }
  
  // Also start when tokens are set
  const originalSetItem = localStorage.setItem
  localStorage.setItem = function(key, _value) {
    originalSetItem.apply(this, arguments)
    if (key === 'access_token' && localStorage.getItem('refresh_token')) {
      if (!tokenRefreshInterval) {
        startProactiveTokenRefresh()
      }
    }
  }
  
  // Stop when tokens are removed
  const originalRemoveItem = localStorage.removeItem
  localStorage.removeItem = function(key) {
    originalRemoveItem.apply(this, arguments)
    if (key === 'access_token' || key === 'refresh_token') {
      if (!localStorage.getItem('access_token') || !localStorage.getItem('refresh_token')) {
        stopProactiveTokenRefresh()
      }
    }
  }
}

// Request interceptor - add auth token, cache check, and mask endpoints
apiClient.interceptors.request.use(
  (config) => {
    // Check cache for GET requests (skip cache if _skipCache flag is set)
    if (config.method === 'get' && !config._skipCache) {
      const cached = getCachedResponse(config)
      if (cached) {
        // Return cached response
        return Promise.reject({
          __cached: true,
          data: cached,
          status: 200,
          statusText: 'OK',
          headers: {},
          config
        })
      }
    }
    
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add tenant/website header if available
    const website = localStorage.getItem('current_website')
    if (website) {
      config.headers['X-Website'] = website
    }
    
    // If data is FormData, remove Content-Type header to let browser set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    // Endpoint masking with backend proxy
    // When enabled, endpoints are masked and routed through /api/v1/proxy/
    const enableMasking = import.meta.env.VITE_ENABLE_ENDPOINT_MASKING === 'true'
    
    if (enableMasking && config.url) {
      // Store original URL for debugging
      config._originalUrl = config.url
      
      // Get user role
      const userRole = getUserRole()
      
      // Admins and superadmins bypass masking
      if (userRole === 'admin' || userRole === 'superadmin') {
        // No masking for admins
      } else {
        // Check if endpoint should be blocked (admin-only endpoints for non-admins)
        const shouldBlock = (userRole === 'client' || userRole === 'writer') && 
                           (config.url.includes('/admin-management/') || 
                            config.url.includes('/superadmin-management/'))
        
        if (shouldBlock) {
          // Block access to admin endpoints for non-admins
          return Promise.reject({
            response: {
              status: 403,
              data: { error: 'Access denied. This endpoint is not available for your role.' }
            }
          })
        }
        
        // Mask the endpoint and route through proxy
        const masked = maskEndpoint(config.url)
        if (masked !== config.url && !masked.includes('/restricted/')) {
          // Route through proxy: /api/v1/proxy/{masked_path}
          // Remove /api/v1 prefix from masked endpoint if present
          let proxyPath = masked.startsWith('/api/v1/') 
            ? masked.slice(7)  // Remove '/api/v1'
            : masked.startsWith('/') 
              ? masked.slice(1)  // Remove leading '/'
              : masked
          
          config.url = `/api/v1/proxy/${proxyPath}`
        }
      }
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle caching, token refresh and retries
apiClient.interceptors.response.use(
  (response) => {
    // Cache successful GET responses (skip cache if _skipCache flag is set)
    if (response.config.method === 'get' && !response.config._skipCache) {
      // Determine TTL based on endpoint
      let ttl = 5 * 60 * 1000 // Default 5 minutes
      
      // Longer cache for dashboard/analytics data
      if (response.config.url?.includes('/dashboard/') || 
          response.config.url?.includes('/analytics/') ||
          response.config.url?.includes('/stats/')) {
        ttl = 2 * 60 * 1000 // 2 minutes for dashboard data
      }
      
      // Shorter cache for lists that change frequently
      // Check if URL includes '/orders/' but doesn't have a number (i.e., it's a list, not a detail page)
      if (response.config.url?.includes('/orders/') && 
          !/\d+/.test(response.config.url)) {
        ttl = 1 * 60 * 1000 // 1 minute for order lists
      }
      
      cacheResponse(response.config, response.data, ttl)
    }
    
    return response
  },
  async (error) => {
    // Handle cached responses
    if (error.__cached) {
      return Promise.resolve({
        data: error.data,
        status: error.status,
        statusText: error.statusText,
        headers: error.headers,
        config: error.config
      })
    }
    
    const originalRequest = error.config

    // Simple retry for network errors (once)
    if (!error.response && !originalRequest._retry_network) {
      originalRequest._retry_network = true
      return apiClient(originalRequest)
    }

    // Handle 401 Unauthorized - refresh token
    if (isAuthError(error) && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          // No refresh token - only logout if this was not a refresh token request itself
          if (!originalRequest.url?.includes('refresh-token')) {
            console.warn('No refresh token available, clearing auth')
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('current_website')
            localStorage.removeItem('user')
            // Don't redirect if we're on a guest/public route
            const isGuestRoute = window.location.pathname.startsWith('/guest-orders') ||
                                  window.location.pathname.startsWith('/blog') ||
                                  window.location.pathname.startsWith('/page') ||
                                  window.location.pathname === '/terms'
            if (window.location.pathname !== '/login' && !isGuestRoute) {
              window.location.href = '/login'
            }
          }
          return Promise.reject(error)
        }

        // Use the same baseURL as apiClient
        const baseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_FULL_URL || '/api/v1'
        const refreshURL = baseURL.endsWith('/api/v1') 
          ? `${baseURL}/auth/auth/refresh-token/`
          : `${baseURL}/api/v1/auth/auth/refresh-token/`

        const response = await axios.post(
          refreshURL,
          { refresh_token: refreshToken },
          {
            headers: {
              'Content-Type': 'application/json',
            }
          }
        )
        
        const { access_token } = response.data
        if (access_token) {
          localStorage.setItem('access_token', access_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } else {
          throw new Error('No access token in refresh response')
        }
      } catch (refreshError) {
        // Only logout if refresh token is actually invalid/expired (401/403)
        // Don't logout on network errors or other issues
        const isTokenInvalid = refreshError.response?.status === 401 || 
                               refreshError.response?.status === 403 ||
                               refreshError.response?.data?.code === 'token_not_valid'
        
        if (isTokenInvalid) {
          console.warn('Refresh token invalid, logging out')
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('current_website')
          localStorage.removeItem('user')
          localStorage.removeItem('website_id')
          sessionStorage.clear()
          
          // Only redirect if not already on login page or guest route
          const isGuestRoute = window.location.pathname.startsWith('/guest-orders') ||
                                window.location.pathname.startsWith('/blog') ||
                                window.location.pathname.startsWith('/page') ||
                                window.location.pathname === '/terms'
          if (window.location.pathname !== '/login' && !isGuestRoute) {
            window.location.replace('/login')
          }
        } else {
          // For network errors or other issues, just reject the original error
          // Only log if it's not a rate limit (429) - those are expected
          if (refreshError.response?.status !== 429) {
            console.warn('Token refresh failed (non-auth error):', refreshError.message)
          }
        }
        
        return Promise.reject(error) // Return original error, not refresh error
      }
    }

    // Invalidate cache on mutations (POST, PUT, PATCH, DELETE)
    if (originalRequest && originalRequest.method !== 'get') {
      if (originalRequest.url) {
        invalidateCache(originalRequest.url)
        // Also invalidate related dashboard/analytics caches
        if (originalRequest.url.includes('/orders/') || 
            originalRequest.url.includes('/payments/') ||
            originalRequest.url.includes('/users/') ||
            originalRequest.url.includes('/writers/')) {
          invalidateCache('/dashboard/')
          invalidateCache('/analytics/')
          invalidateCache('/stats/')
        }
      }
    }
    
    // Suppress noisy backend errors (404/403/429) for known missing endpoints
    // These are expected and don't need to spam the console
    const status = error.response?.status
    const url = error.config?.url || error.request?.responseURL || ''
    
    // Known missing/restricted endpoints that are expected to fail
    const expectedFailures = [
      '/writer-management/writer-order-hold-requests/',
      '/client-wallet/client-wallet/my_wallet/',
      '/notifications_system/notifications/feed/',
      '/order-configs/academic-levels/',
      '/order-configs/paper-types/',
      '/order-configs/types-of-work/',
      '/order-configs/subjects/',
      '/auth/auth/refresh-token/',
      '/order-files/order-files/',
      '/order-files/extra-service-files/',
      '/client-management/dashboard/enhanced-order-status/',
      '/orders/progress/order/',
      '/writer-management/writers/my_profile/',
      '/writer-management/writer-profiles/',
      '/writer-management/writer-resources/',
      '/writer-management/writer-resource-categories/',
      '/writer-management/badge-performance/',
      '/writer-management/dashboard/communications/',
      '/writer-wallet/writer-wallets/',
      '/order-communications/communication-threads/',
      '/users/users/profile/',
      '/orders/draft-requests/check-eligibility/',
      '/admin-management/dashboard/top-clients/',
      '/order-communications/communication-threads-stream/',
    ]
    
    const isExpectedFailure = expectedFailures.some(endpoint => url.includes(endpoint))
    
    // Only suppress if it's an expected failure with a known status code
    if (isExpectedFailure && (status === 404 || status === 403 || status === 429)) {
      // Silently handle - these are backend configuration issues, not frontend bugs
      // Return a normalized error but don't log it to console
      const normalizedError = normalizeApiError(error)
      normalizedError._suppressLog = true
      return Promise.reject(normalizedError)
    }
    
    // Normalize other errors
    return Promise.reject(normalizeApiError(error))
  }
)

export default apiClient

