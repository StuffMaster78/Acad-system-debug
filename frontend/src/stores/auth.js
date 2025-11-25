/**
 * Pinia Auth Store
 * 
 * Authentication state management using Pinia.
 * Copy this to: src/stores/auth.js
 */

import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    loading: false,
    error: null
  }),

  getters: {
    // Check if user is authenticated
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    
    // Get user role
    userRole: (state) => state.user?.role || null,
    
    // Check if user is admin
    isAdmin: (state) => {
      const role = state.user?.role
      return role === 'admin' || role === 'superadmin'
    },
    
    // Check if user is superadmin
    isSuperAdmin: (state) => state.user?.role === 'superadmin',

    // Check if user is writer
    isWriter: (state) => state.user?.role === 'writer',

    // Check if user is client
    isClient: (state) => state.user?.role === 'client',

    // Check if user is editor
    isEditor: (state) => state.user?.role === 'editor',

    // Check if user is support staff
    isSupport: (state) => state.user?.role === 'support',
    
    // Get user email
    userEmail: (state) => state.user?.email || null,
    
    // Get user full name
    userFullName: (state) => state.user?.full_name || null,
    
    // Get website ID
    websiteId: (state) => state.user?.website_id || null
  },

  actions: {
    /**
     * Set authentication tokens
     */
    async setTokens({ accessToken, refreshToken }) {
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      
      // Store in localStorage
      if (accessToken) {
        localStorage.setItem('access_token', accessToken)
      }
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
      }
    },

    /**
     * Set user data
     */
    async setUser(user) {
      this.user = user
      
      // Store in localStorage
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
        
        // Store website ID if available
        if (user.website_id) {
          localStorage.setItem('website_id', user.website_id)
        }
      }
    },

    /**
     * Login user
     */
    async login(email, password, rememberMe = false) {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.login(email, password, rememberMe)
        
        // Check if 2FA is required
        if (response.data.requires_2fa) {
          return {
            requires2FA: true,
            sessionId: response.data.session_id
          }
        }

        // Set tokens and user
        await this.setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token
        })
        await this.setUser(response.data.user)
        
        return {
          success: true,
          user: response.data.user
        }
      } catch (error) {
        this.error = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    'Login failed. Please check your credentials.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Verify 2FA code
     */
    async verify2FA(code, sessionId) {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.verify2FA(code)
        
        // Set tokens and user
        await this.setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token
        })
        await this.setUser(response.data.user)
        
        return {
            success: true,
            user: response.data.user
        }
      } catch (error) {
        this.error = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    'Invalid code. Please try again.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Logout user
     */
    async logout(logoutAll = false) {
      this.loading = true
      this.error = null

      try {
        // Call logout API if authenticated
        if (this.isAuthenticated) {
          await authApi.logout(logoutAll)
        }
      } catch (error) {
        console.error('Logout error:', error)
        // Continue with logout even if API call fails
      } finally {
        // Clear state
        this.user = null
        this.accessToken = null
        this.refreshToken = null
        
        // Clear localStorage
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        localStorage.removeItem('website_id')
        
        this.loading = false
        
        // Redirect to login
        router.push('/login')
      }
    },

    /**
     * Change password
     */
    async changePassword(currentPassword, newPassword, confirmPassword) {
      this.loading = true
      this.error = null

      try {
        await authApi.changePassword(currentPassword, newPassword, confirmPassword)
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    'Failed to change password.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Request password reset
     */
    async requestPasswordReset(email) {
      this.loading = true
      this.error = null

      try {
        await authApi.requestPasswordReset(email)
        return { success: true }
      } catch (error) {
        // Always return success for security (don't reveal if email exists)
        return { success: true }
      } finally {
        this.loading = false
      }
    },

    /**
     * Confirm password reset
     */
    async confirmPasswordReset(token, password) {
      this.loading = true
      this.error = null

      try {
        await authApi.confirmPasswordReset(token, password)
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    'Failed to reset password.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Request magic link
     */
    async requestMagicLink(email) {
      this.loading = true
      this.error = null

      try {
        await authApi.requestMagicLink(email)
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    'Failed to send magic link.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Verify magic link
     */
    async verifyMagicLink(token) {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.verifyMagicLink(token)
        
        // Set tokens and user
        await this.setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token
        })
        await this.setUser(response.data.user)
        
        return {
            success: true,
            user: response.data.user
        }
      } catch (error) {
        this.error = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    'Invalid or expired magic link.'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Load user from localStorage
     */
    loadFromStorage() {
      try {
        const accessToken = localStorage.getItem('access_token')
        const refreshToken = localStorage.getItem('refresh_token')
        const userStr = localStorage.getItem('user')

        if (accessToken && refreshToken && userStr) {
          this.accessToken = accessToken
          this.refreshToken = refreshToken
          this.user = JSON.parse(userStr)
        }
      } catch (error) {
        console.error('Failed to load from storage:', error)
        // Clear invalid data
        this.clearStorage()
      }
    },

    /**
     * Clear all storage
     */
    clearStorage() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      localStorage.removeItem('website_id')
    },

    /**
     * Refresh user data
     */
    async refreshUser() {
      try {
        const response = await authApi.getCurrentUser()
        await this.setUser(response.data)
      } catch (error) {
        console.error('Failed to refresh user:', error)
        // If refresh fails, user might be logged out
        if (error.response?.status === 401) {
          await this.logout()
        }
      }
    },

    /**
     * Fetch current user from API (alias for refreshUser for router compatibility)
     */
    async fetchUser() {
      return this.refreshUser()
    }
  }
})
