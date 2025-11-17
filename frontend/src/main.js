/**
 * Vue Application Entry Point
 * 
 * Main application setup with Pinia, Router, and global configuration.
 * Copy this to: src/main.js
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import global styles
import './styles/dashboard.css'

// Create Vue app
const app = createApp(App)

// Install Pinia for state management
const pinia = createPinia()
app.use(pinia)

// Install Router
app.use(router)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err, info)
  // Could send to error tracking service (e.g., Sentry)
}

// Global properties (if needed)
// app.config.globalProperties.$api = apiClient

// Mount app
app.mount('#app')

// Load auth state from storage on app start
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.loadFromStorage()
