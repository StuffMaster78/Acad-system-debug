import apiClient from './client'

export default {
  // Login
  login: (credentials) => apiClient.post('/auth/auth/login/', credentials),
  
  // Register
  register: (data) => apiClient.post('/auth/auth/register/', data),
  
  // Password reset
  requestPasswordReset: (email) => apiClient.post('/auth/auth/password/reset/', { email }),
  resetPassword: (data) => apiClient.post('/auth/auth/password/reset/confirm/', data),
  
  // Token refresh
  refreshToken: (refreshToken) => apiClient.post('/auth/auth/refresh-token/', { 
    refresh: refreshToken 
  }),
  
  // Logout
  logout: () => apiClient.post('/auth/auth/logout/'),
  
  // Get current user
  getCurrentUser: () => apiClient.get('/users/users/profile/'),
}

