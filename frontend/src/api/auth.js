import apiClient from './client'
import axios from 'axios'

// Create a public API client without auth token for registration
const publicApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_FULL_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// Export both authAPI and authApi for compatibility
export const authAPI = {
  login: (email, password, rememberMe = false) => {
    console.log('📤 Login API call:', {
      url: '/auth/auth/login/',
      baseURL: apiClient.defaults.baseURL,
      email,
      remember_me: rememberMe,
    })
    return apiClient.post('/auth/auth/login/', {
      email,
      password,
      remember_me: rememberMe,
    })
      .then(response => {
        console.log('✅ Login API success:', {
          status: response.status,
          data: { ...response.data, password: '***' },
        })
        return response
      })
      .catch(error => {
        console.error('❌ Login API error:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          url: error.config?.url,
          baseURL: error.config?.baseURL,
        })
        throw error
      })
  },

  logout: (logoutAll = false) => {
    const params = logoutAll ? { logout_all: 'true' } : {}
    return apiClient.post('/auth/auth/logout/', null, { params })
  },

  refreshToken: (refreshToken) => {
    return apiClient.post('/auth/auth/refresh-token/', {
      refresh_token: refreshToken,
    })
  },

  getProfile: () => {
    return apiClient.get('/users/users/profile/')
  },

  // Get current user profile (from auth endpoint)
  getCurrentUser: () => {
    return apiClient.get('/auth/auth/user/')
  },

  // Update current user profile
  updateProfile: (data) => {
    // Content-Type header will be handled by the request interceptor for FormData
    return apiClient.patch('/auth/auth/user/', data)
  },

  // Impersonation (admin/superadmin only)
  impersonate: (userId) => {
    return apiClient.post('/auth/impersonate/', { user_id: userId })
  },

  // Create impersonation token (for new tab impersonation)
  createImpersonationToken: (userId) => {
    return apiClient.post('/auth/impersonate/create_token/', { target_user: userId })
  },

  // Start impersonation with token
  startImpersonation: (token) => {
    return apiClient.post('/auth/impersonate/start/', { token })
  },

  endImpersonation: (data = {}) => {
    return apiClient.post('/auth/impersonate/end/', data)
  },

  getImpersonationStatus: () => {
    return apiClient.get('/auth/impersonate/status/')
  },

  signup: (data) => {
    // Use public client (no auth token) for registration
    // Some environments expose nested route /auth/auth/register/
    // Try that first, then fall back to /auth/register/
    const primary = '/auth/auth/register/'
    const fallback = '/auth/register/'
    console.log('Signup API call:', { url: primary, baseURL: publicApiClient.defaults.baseURL, data: { ...data, password: '***' } })
    
    return publicApiClient.post(primary, data)
      .then(response => {
        console.log('Signup API success:', response.status, response.data)
        return response
      })
      .catch(error => {
        // Fallback to alternative route if 404
        if (error?.response?.status === 404) {
          return publicApiClient.post(fallback, data)
        }
        console.error('Signup API error:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          url: error.config?.url,
          baseURL: error.config?.baseURL
        })
        
        // Improve error handling for network errors
        if (!error.response) {
          // Network error - server not reachable
          const errorMsg = `Network error: Unable to connect to ${publicApiClient.defaults.baseURL}. Please ensure the backend is running at ${publicApiClient.defaults.baseURL.replace('/api/v1', '')}`
          throw new Error(errorMsg)
        }
        throw error
      })
  },

  requestPasswordReset: (email) => {
    return apiClient.post('/auth/auth/password-reset/', { email })
  },
  confirmPasswordReset: (token, password) => {
    return apiClient.post('/auth/auth/password-reset/confirm/', { token, password })
  },

  // Password change (authenticated)
  changePassword: (currentPassword, newPassword, confirmPassword) => {
    return apiClient.post('/auth/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  },

  // Magic link login
  requestMagicLink: (email) => {
    return publicApiClient.post('/auth/magic-link/request/', { email })
  },

  verifyMagicLink: (token) => {
    return publicApiClient.post('/auth/magic-link/verify/', { token })
  },

  // 2FA
  setup2FA: () => {
    return apiClient.post('/auth/2fa/totp/setup/')
  },

  verify2FA: (code) => {
    return apiClient.post('/auth/2fa/totp/verify/', { code })
  },

  // Session management
  getActiveSessions: () => {
    return apiClient.get('/auth/user-sessions/')
  },
  getSessions: () => {
    return apiClient.get('/auth/user-sessions/')
  },
  revokeSession: (sessionId) => {
    return apiClient.delete(`/auth/user-sessions/${sessionId}/`)
  },
  revokeAllSessions: () => {
    return apiClient.post('/auth/user-sessions/revoke-all/')
  },
  
  // Login Sessions (LoginSession model)
  getLoginSessions: () => {
    // Try session-management first, fallback to user-login-sessions
    return apiClient.get('/auth/user-login-sessions/').catch(() => {
      return apiClient.get('/auth/session-management/current_sessions/')
    })
  },
  revokeLoginSession: (sessionId) => {
    return apiClient.post(`/auth/user-login-sessions/${sessionId}/revoke/`)
  },
  revokeAllLoginSessions: (keepCurrent = true) => {
    return apiClient.post('/auth/user-login-sessions/revoke-all/', null, {
      params: { keep_current: keepCurrent ? '1' : '0' }
    })
  },
  updateDeviceName: (sessionId, deviceName) => {
    return apiClient.patch(`/auth/user-login-sessions/${sessionId}/update-device-name/`, {
      device_name: deviceName
    })
  },
  reportSuspiciousSession: (sessionId, reason = 'This wasn\'t me') => {
    return apiClient.post(`/auth/user-login-sessions/${sessionId}/report-suspicious/`, {
      reason
    })
  },

  // Account unlock
  requestAccountUnlock: (email) => {
    return publicApiClient.post('/auth/auth/account-unlock/', { email })
  },

  confirmAccountUnlock: (token) => {
    return publicApiClient.post('/auth/auth/account-unlock/confirm/', { token })
  },
}

// Alias for compatibility with components using authApi
export const authApi = authAPI

