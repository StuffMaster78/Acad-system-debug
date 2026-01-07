/**
 * Pinia Auth Store
 * 
 * Authentication state management using Pinia.
 * Copy this to: src/stores/auth.js
 */

import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import router from '@/router'
import usersApi from '@/api/users'
import { detectAndStoreTimezone, getBrowserTimezone } from '@/composables/useTimezone'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    loading: false,
    error: null,
    isImpersonating: false,
    impersonator: null
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
    async syncTimezoneWithBackend() {
      try {
        const timezone = await detectAndStoreTimezone()
        if (!timezone) {
          return
        }

        // Avoid unnecessary API calls if we already know backend uses this timezone
        const userTimezone = this.user?.timezone || this.user?.client_timezone || this.user?.writer_timezone
        if (userTimezone === timezone) {
          return
        }

        await usersApi.updateTimezone(timezone)
      } catch (error) {
        // Non-fatal: timezone sync should never break auth flow
        console.warn('Failed to sync timezone with backend', error)
      }
    },

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

      // Best-effort timezone sync whenever we have a user
      if (user) {
        // Fire and forget
        this.syncTimezoneWithBackend()
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
        const data = response.data || {}
        
        // Check if 2FA is required
        if (data.requires_2fa) {
          return {
            requires2FA: true,
            sessionId: data.session_id
          }
        }

        // Support both legacy (`access_token`/`refresh_token`) and new (`access`/`refresh`) keys.
        const accessToken = data.access_token || data.access
        const refreshToken = data.refresh_token || data.refresh

        await this.setTokens({
          accessToken,
          refreshToken
        })
        await this.setUser(data.user)
        
        return {
          success: true,
          user: data.user
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
        const data = response.data || {}
        
        const accessToken = data.access_token || data.access
        const refreshToken = data.refresh_token || data.refresh

        // Set tokens and user
        await this.setTokens({
          accessToken,
          refreshToken
        })
        await this.setUser(data.user)
        
        return {
            success: true,
            user: data.user
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
        if (this.isAuthenticated && this.accessToken) {
          try {
            await authApi.logout(logoutAll)
          } catch (error) {
            // Log but don't throw - continue with local cleanup
            console.warn('Logout API call failed, continuing with local cleanup:', error)
          }
        }
      } catch (error) {
        console.error('Logout error:', error)
        // Continue with logout even if API call fails
      } finally {
        // Stop any ongoing processes
        try {
          // Clear any intervals or timeouts
          if (this._refreshInterval) {
            clearInterval(this._refreshInterval)
            this._refreshInterval = null
          }
        } catch (e) {
          // Ignore cleanup errors
        }
        
        // Clear state
        this.user = null
        this.accessToken = null
        this.refreshToken = null
        
        // Clear localStorage completely
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        localStorage.removeItem('website_id')
        localStorage.removeItem('remember_me')
        
        // Clear sessionStorage as well
        sessionStorage.clear()
        
        this.loading = false
        
        // Force redirect to login (use replace to prevent back button issues)
        // Use setTimeout to ensure state is cleared before redirect
        setTimeout(() => {
          if (router.currentRoute.value.path !== '/login') {
            router.replace('/login').catch(() => {
              // Fallback if router fails - force page reload
              window.location.replace('/login')
            })
          } else {
            // If already on login, force reload to clear any cached state
            window.location.reload()
          }
        }, 100)
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
     * This is called on app initialization to restore auth state after page refresh
     */
    loadFromStorage() {
      try {
        const accessToken = localStorage.getItem('access_token')
        const refreshToken = localStorage.getItem('refresh_token')
        const userStr = localStorage.getItem('user')

        // Restore tokens if they exist
        if (accessToken) {
          this.accessToken = accessToken
        }
        if (refreshToken) {
          this.refreshToken = refreshToken
        }

        // Restore user data if it exists
        if (userStr) {
          try {
            this.user = JSON.parse(userStr)
          } catch (parseError) {
            console.error('Failed to parse user data from storage:', parseError)
            // If user data is corrupted, try to fetch it from API if we have tokens
            if (accessToken && refreshToken) {
              // User data will be fetched in router guard if needed
              this.user = null
            } else {
              // No tokens, clear everything
              this.clearStorage()
            }
          }
        } else if (accessToken && refreshToken) {
          // We have tokens but no user data - this is okay, user will be fetched in router guard
          this.user = null
        } else {
          // No tokens and no user - clear everything
          this.clearStorage()
        }
        
        // Restore impersonation state if it exists
        const isImpersonating = localStorage.getItem('is_impersonating') === 'true'
        const impersonatorStr = localStorage.getItem('impersonator')
        
        if (isImpersonating) {
          this.isImpersonating = true
          if (impersonatorStr) {
            try {
              this.impersonator = JSON.parse(impersonatorStr)
            } catch (parseError) {
              console.error('Failed to parse impersonator data from storage:', parseError)
              this.impersonator = null
            }
          }
        } else {
          this.isImpersonating = false
          this.impersonator = null
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
      localStorage.removeItem('is_impersonating')
      localStorage.removeItem('impersonator')
      this.isImpersonating = false
      this.impersonator = null
    },

    /**
     * End impersonation and restore admin session
     * If called from an impersonation tab, closes the tab and returns focus to parent
     */
    async endImpersonation() {
      this.loading = true
      this.error = null

      // Check if this is an impersonation tab FIRST (before making API call)
      const isImpersonationTab = localStorage.getItem('_is_impersonation_tab') === 'true'

      try {
        // Call API to end impersonation with close_tab flag
        const response = await authApi.endImpersonation({ close_tab: isImpersonationTab })
        
        // Track impersonation end event (for auditing)
        try {
          if (typeof window !== 'undefined' && window.gtag) {
            window.gtag('event', 'impersonation_end', {
              event_category: 'admin',
              event_label: isImpersonationTab ? 'tab_close' : 'manual_end'
            })
          }
        } catch (analyticsError) {
          // Analytics failure shouldn't block the flow
          if (import.meta.env.DEV) {
            console.warn('Analytics tracking failed:', analyticsError)
          }
        }
        
        // If this is an impersonation tab, we should close it WITHOUT updating tokens
        // The parent tab (admin) should remain logged in with its own session
        if (isImpersonationTab) {
          // Get impersonator info BEFORE clearing it (to determine dashboard route)
          let impersonatorRole = null
          let impersonatorId = null
          try {
            const impersonatorStr = localStorage.getItem('impersonator')
            if (impersonatorStr) {
              const impersonator = JSON.parse(impersonatorStr)
              impersonatorRole = impersonator?.role || null
              impersonatorId = impersonator?.id || null
            }
          } catch (e) {
            if (import.meta.env.DEV) {
              console.warn('Could not parse impersonator from localStorage:', e)
            }
          }
          
          // Clear the flag immediately
          localStorage.removeItem('_is_impersonation_tab')
          
          // Clear impersonation flags locally (but don't update tokens/user)
          this.isImpersonating = false
          this.impersonator = null
          localStorage.removeItem('is_impersonating')
          localStorage.removeItem('impersonator')
          
          // Determine dashboard route based on impersonator role
          let dashboardRoute = '/dashboard' // Default dashboard
          if (impersonatorRole === 'admin') {
            dashboardRoute = '/admin/dashboard'
          } else if (impersonatorRole === 'superadmin') {
            dashboardRoute = '/admin/superadmin'
          } else if (impersonatorRole === 'support') {
            dashboardRoute = '/dashboard' // Support uses main dashboard
          }
          
          // Try to close the tab and return focus to parent, redirecting to dashboard
          let redirectSuccess = false
          let closeSuccess = false
          
          if (window.opener && !window.opener.closed) {
            try {
              // Redirect parent window to appropriate dashboard
              try {
                window.opener.location.href = dashboardRoute
                redirectSuccess = true
              } catch (e) {
                // If we can't set location directly, try using postMessage
                if (import.meta.env.DEV) {
                  console.warn('Could not redirect parent window directly, trying postMessage:', e)
                }
                window.opener.postMessage({ type: 'redirect', path: dashboardRoute }, window.location.origin)
                redirectSuccess = true // Assume postMessage will work
              }
              
              // Focus the parent window (admin tab) first
              window.opener.focus()
              
              // Close this impersonation tab
              // Use a small delay to ensure redirect and focus happen first
              setTimeout(() => {
                try {
                  window.close()
                  closeSuccess = true
                } catch (closeError) {
                  // Browser blocked window.close() - show user-friendly message
                  if (import.meta.env.DEV) {
                    console.warn('Browser blocked window.close():', closeError)
                  }
                  // Show notification that user should manually close the tab
                  this.error = 'Impersonation ended. Please close this tab manually to return to your dashboard.'
                  // Still try to redirect this window as fallback
                  setTimeout(() => {
                    router.push(dashboardRoute)
                  }, 2000)
                }
              }, 300)
            } catch (e) {
              // Comprehensive error handling
              const errorMessage = e?.message || 'Unknown error'
              if (import.meta.env.DEV) {
                console.error('Error during impersonation end:', errorMessage, e)
              }
              
              // Still try to redirect even if we can't close
              if (!redirectSuccess) {
                try {
                  window.opener.location.href = dashboardRoute
                  redirectSuccess = true
                } catch (redirectError) {
                  // Last resort: use postMessage
                  try {
                    window.opener.postMessage({ type: 'redirect', path: dashboardRoute }, window.location.origin)
                    redirectSuccess = true
                  } catch (postMessageError) {
                    this.error = 'Impersonation ended, but could not redirect. Please manually navigate to your dashboard.'
                    // Fallback: redirect this window
                    router.push(dashboardRoute)
                  }
                }
              }
              
              // If redirect succeeded but close failed, inform user
              if (redirectSuccess && !closeSuccess) {
                this.error = 'Impersonation ended. Please close this tab manually.'
              }
            }
          } else {
            // No parent window - redirect this window to dashboard instead
            if (import.meta.env.DEV) {
              console.warn('No parent window found for impersonation tab, redirecting this window')
            }
            router.push(dashboardRoute)
            redirectSuccess = true
          }
          
          // Return early - don't update tokens/user state in impersonation tab
          return { 
            success: true, 
            redirectSuccess,
            closeSuccess,
            message: redirectSuccess ? 'Impersonation ended successfully' : 'Impersonation ended, but redirect failed'
          }
        }
        
        // If NOT an impersonation tab (ending impersonation from admin tab itself),
        // update tokens and user with admin's data
        // Only update if close_tab is false (same-tab ending)
        if (!response.data.close_tab) {
          if (response.data.access_token && response.data.refresh_token) {
            await this.setTokens({
              accessToken: response.data.access_token,
              refreshToken: response.data.refresh_token
            })
          }
          
          if (response.data.user) {
            await this.setUser(response.data.user)
          }
        }
        
        // Clear impersonation flags
        this.isImpersonating = false
        this.impersonator = null
        localStorage.removeItem('is_impersonating')
        localStorage.removeItem('impersonator')
        
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    'Failed to end impersonation.'
        
        // Even if API fails, clear impersonation state locally
        this.isImpersonating = false
        this.impersonator = null
        localStorage.removeItem('is_impersonating')
        localStorage.removeItem('impersonator')
        
        // Only clear tab flag if it was set
        if (isImpersonationTab) {
          localStorage.removeItem('_is_impersonation_tab')
        }
        
        throw error
      } finally {
        this.loading = false
      }
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
