import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './assets/main.css'

const app = createApp(App)

// Use plugins
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Initialize auth store from localStorage
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.loadFromStorage()

app.mount('#app')

