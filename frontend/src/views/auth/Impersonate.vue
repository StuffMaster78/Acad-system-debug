<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Starting Impersonation
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Please wait while we log you in as the user...
        </p>
      </div>

      <div v-if="loading" class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-sm text-gray-600">Authenticating...</p>
      </div>

      <div v-if="error" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Impersonation Failed</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ error }}</p>
            </div>
            <div class="mt-4">
              <button
                @click="retry"
                class="text-sm font-medium text-red-800 hover:text-red-900 underline"
              >
                Try again
              </button>
              <span class="mx-2 text-red-400">|</span>
              <button
                @click="closeWindow"
                class="text-sm font-medium text-red-800 hover:text-red-900 underline"
              >
                Close window
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref(null)

const startImpersonation = async () => {
  const token = route.query.token
  
  if (!token) {
    error.value = 'No impersonation token provided. Please generate a new token.'
    loading.value = false
    return
  }

  try {
    // Get admin token from localStorage (stored by the admin tab)
    // Using localStorage so it's accessible across tabs
    const adminTokenData = localStorage.getItem('_impersonation_admin_token')
    
    if (!adminTokenData) {
      error.value = 'Admin session not found. Please try impersonating again from the admin panel.'
      loading.value = false
      return
    }
    
    const { token: adminToken, expiresAt } = JSON.parse(adminTokenData)
    
    // Check if token expired
    if (Date.now() > expiresAt) {
      localStorage.removeItem('_impersonation_admin_token')
      error.value = 'Admin session expired. Please try impersonating again from the admin panel.'
      loading.value = false
      return
    }
    
    // Temporarily set admin token for the API call
    // The apiClient interceptor will automatically use the token from localStorage
    const originalToken = localStorage.getItem('access_token')
    localStorage.setItem('access_token', adminToken)
    
    try {
      // Start impersonation with the admin token
      // Create a temporary axios instance with the admin token for this call
      const axios = (await import('axios')).default
      const baseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_FULL_URL || '/api/v1'
      const startUrl = baseURL.endsWith('/api/v1') 
        ? `${baseURL}/auth/impersonate/start/`
        : `${baseURL}/api/v1/auth/impersonate/start/`
      
      const response = await axios.post(
        startUrl,
        { token },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${adminToken}`
          }
        }
      )
      
      const { access_token, refresh_token, user, impersonation } = response.data
      
      // Store the new tokens (for the impersonated user) - use store actions for reactivity
      await authStore.setTokens({ accessToken: access_token, refreshToken: refresh_token })
      await authStore.setUser(user)
      
      // Set impersonation flags
      authStore.isImpersonating = true
      authStore.impersonator = impersonation?.impersonated_by || null

      // Also store in localStorage for persistence
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('is_impersonating', 'true')
      if (impersonation?.impersonated_by) {
        localStorage.setItem('impersonator', JSON.stringify(impersonation.impersonated_by))
      }
      
      // Clear the temporary admin token
      localStorage.removeItem('_impersonation_admin_token')
      
      // Set flag to indicate this is an impersonation tab (for closing later)
      localStorage.setItem('_is_impersonation_tab', 'true')
      
      // Wait for Vue reactivity to update - use nextTick to ensure store is reactive
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))
      
      // Verify auth store is updated
      if (!authStore.isAuthenticated || !authStore.user) {
        console.error('Auth store not updated after impersonation', {
          isAuthenticated: authStore.isAuthenticated,
          hasUser: !!authStore.user,
          hasToken: !!authStore.accessToken,
          userRole: authStore.userRole
        })
        error.value = 'Failed to authenticate. Please try again.'
        loading.value = false
        return
      }
      
      // Determine role-specific dashboard route
      const userRole = user?.role || authStore.userRole
      let dashboardRoute = '/dashboard' // Default fallback
      
      if (userRole === 'client') {
        dashboardRoute = '/client' // Client dashboard
      } else if (userRole === 'writer') {
        dashboardRoute = '/dashboard' // Writers use main dashboard
      } else if (userRole === 'admin') {
        dashboardRoute = '/admin/dashboard' // Admin dashboard
      } else if (userRole === 'superadmin') {
        dashboardRoute = '/superadmin/dashboard' // Superadmin dashboard
      } else if (userRole === 'editor') {
        dashboardRoute = '/dashboard' // Editors use main dashboard
      } else if (userRole === 'support') {
        dashboardRoute = '/dashboard' // Support uses main dashboard
      }
      
      loading.value = false
      
      // Use window.location for a hard redirect to ensure router guard runs with fresh state
      // This ensures the router guard sees the updated auth store
      window.location.href = dashboardRoute
    } catch (apiErr) {
      // Restore original token if impersonation fails (if there was one)
      if (originalToken) {
        localStorage.setItem('access_token', originalToken)
      } else {
        localStorage.removeItem('access_token')
      }
      throw apiErr
    }
  } catch (err) {
    console.error('Impersonation error:', err)
    error.value = err.response?.data?.error || 
                  err.response?.data?.detail || 
                  'Failed to start impersonation. The token may be invalid or expired.'
    loading.value = false
    // Clear the temporary admin token on error
    localStorage.removeItem('_impersonation_admin_token')
  }
}

const retry = () => {
  error.value = null
  loading.value = true
  startImpersonation()
}

const closeWindow = () => {
  window.close()
}

onMounted(() => {
  startImpersonation()
})
</script>

<style scoped>
/* Add any custom styles if needed */
</style>

