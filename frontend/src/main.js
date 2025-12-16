import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './assets/main.css'

// Register lazy image directive
import lazyImageDirective from './directives/lazyImage'

// Register ApexCharts
import VueApexCharts from 'vue3-apexcharts'

// Naive UI
import naive from 'naive-ui'
import { setupNaiveUI } from './plugins/naive-ui'

const app = createApp(App)

// Use plugins
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(VueApexCharts)

// Setup and use Naive UI
setupNaiveUI(app)

// Register global directive
app.directive('lazy-image', lazyImageDirective)

// Initialize auth store from localStorage before mounting
// This ensures authentication state is restored on page refresh
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.loadFromStorage()

app.mount('#app')
