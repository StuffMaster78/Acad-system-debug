import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import VueApexCharts from 'vue3-apexcharts'
import { useAuthStore } from './stores/auth'
import { initTheme } from './composables/useTheme'

// Initialize theme before mounting app so initial paint uses correct mode
initTheme()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(VueApexCharts)

// Load auth state from localStorage before mounting
// This ensures the user stays logged in after page refresh
const authStore = useAuthStore()
authStore.loadFromStorage()

app.mount('#app')
