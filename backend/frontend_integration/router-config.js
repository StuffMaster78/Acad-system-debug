/**
 * Vue Router Configuration with Auth Guards
 * 
 * Router setup with authentication guards and route protection.
 * Copy this to: src/router/index.js
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import components (adjust paths as needed)
const Login = () => import('@/views/auth/Login.vue')
const PasswordChange = () => import('@/views/auth/PasswordChange.vue')
const PasswordReset = () => import('@/views/auth/PasswordReset.vue')
const AccountSettings = () => import('@/views/account/Settings.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const TipManagement = () => import('@/views/admin/TipManagement.vue')

const routes = [
  // Public routes
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      title: 'Login'
    }
  },
  {
    path: '/forgot-password',
    name: 'PasswordReset',
    component: PasswordReset,
    meta: {
      requiresAuth: false,
      title: 'Forgot Password'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'), // Create this component
    meta: {
      requiresAuth: false,
      title: 'Register'
    }
  },

  // Protected routes - require authentication
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/account/password-change',
    name: 'PasswordChange',
    component: PasswordChange,
    meta: {
      requiresAuth: true,
      title: 'Change Password'
    }
  },
  {
    path: '/account/settings',
    name: 'AccountSettings',
    component: AccountSettings,
    meta: {
      requiresAuth: true,
      title: 'Account Settings'
    }
  },

  // Admin routes - require admin role
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'), // Create this component
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Admin Dashboard'
    }
  },
  {
    path: '/admin/tips',
    name: 'TipManagement',
    component: TipManagement,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Tip Management'
    }
  },
  {
    path: '/admin/orders',
    name: 'AdminOrders',
    component: () => import('@/views/admin/Orders.vue'), // Create this component
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Order Management'
    }
  },
  {
    path: '/admin/special-orders',
    name: 'AdminSpecialOrders',
    component: () => import('@/views/admin/SpecialOrders.vue'), // Create this component
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Special Orders'
    }
  },
  {
    path: '/admin/class-bundles',
    name: 'AdminClassBundles',
    component: () => import('@/views/admin/ClassBundles.vue'), // Create this component
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Class Bundles'
    }
  },

  // Superadmin routes - require superadmin role
  {
    path: '/superadmin',
    redirect: '/superadmin/dashboard'
  },
  {
    path: '/superadmin/dashboard',
    name: 'SuperAdminDashboard',
    component: () => import('@/views/superadmin/Dashboard.vue'), // Create this component
    meta: {
      requiresAuth: true,
      requiresSuperAdmin: true,
      title: 'Superadmin Dashboard'
    }
  },

  // 404 catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'), // Create this component
    meta: {
      title: 'Page Not Found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guard - Check authentication and permissions
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Load user from localStorage if not already loaded
  if (!authStore.user && !authStore.isAuthenticated) {
    authStore.loadFromStorage()
  }

  // Set page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - Writing System`
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Not authenticated, redirect to login with return URL
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // Check if route requires admin role
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      // Not admin, redirect to dashboard
      next({ name: 'Dashboard' })
      return
    }

    // Check if route requires superadmin role
    if (to.meta.requiresSuperAdmin && !authStore.isSuperAdmin) {
      // Not superadmin, redirect to dashboard
      next({ name: 'Dashboard' })
      return
    }
  } else {
    // Public route - if already authenticated, redirect to dashboard
    if (to.name === 'Login' && authStore.isAuthenticated) {
      next({ name: 'Dashboard' })
      return
    }
  }

  // All checks passed, proceed to route
  next()
})

// After navigation - Update user data if needed
router.afterEach((to, from) => {
  // Could refresh user data periodically or on specific routes
  // const authStore = useAuthStore()
  // if (authStore.isAuthenticated && to.meta.requiresAuth) {
  //   authStore.refreshUser()
  // }
})

export default router

