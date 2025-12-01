/**
 * Permission checking composable
 * Provides utilities for checking user permissions and roles
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function usePermissionCheck() {
  const authStore = useAuthStore()

  /**
   * Check if user has required role
   */
  const hasRole = (role) => {
    return authStore.userRole === role
  }

  /**
   * Check if user has any of the required roles
   */
  const hasAnyRole = (roles) => {
    if (!Array.isArray(roles)) return false
    return roles.includes(authStore.userRole)
  }

  /**
   * Check if user is admin or superadmin
   */
  const isAdmin = computed(() => {
    return authStore.isAdmin || authStore.isSuperAdmin
  })

  /**
   * Check if user can access resource
   */
  const canAccess = (resource, action = 'view') => {
    // Basic role-based checks
    if (authStore.isSuperAdmin) return true
    
    if (authStore.isAdmin) {
      // Admins can access most resources
      return true
    }
    
    // Add more specific permission checks here
    return false
  }

  /**
   * Get permission error message
   */
  const getPermissionError = () => {
    return {
      message: 'You do not have permission to perform this action.',
      status: 403,
      action: 'Please contact an administrator if you believe this is an error.'
    }
  }

  return {
    hasRole,
    hasAnyRole,
    isAdmin,
    canAccess,
    getPermissionError,
  }
}

