import axios from 'axios'
import { normalizeApiError, isAuthError } from '@/utils/error'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_FULL_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
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
      console.debug('Proactive token refresh failed (non-critical):', error.message)
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

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add tenant/website header if available
    const website = localStorage.getItem('current_website')
    if (website) {
      config.headers['X-Website'] = website
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle token refresh and retries
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
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
          
          // Only redirect if not already on login page or guest route
          const isGuestRoute = window.location.pathname.startsWith('/guest-orders') ||
                                window.location.pathname.startsWith('/blog') ||
                                window.location.pathname.startsWith('/page') ||
                                window.location.pathname === '/terms'
          if (window.location.pathname !== '/login' && !isGuestRoute) {
            window.location.href = '/login'
          }
        } else {
          // For network errors or other issues, just reject the original error
          console.warn('Token refresh failed (non-auth error):', refreshError.message)
        }
        
        return Promise.reject(error) // Return original error, not refresh error
      }
    }

    // Normalize other errors
    return Promise.reject(normalizeApiError(error))
  }
)

export default apiClient

