import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './assets/main.css'

// Register lazy image directive
import lazyImageDirective from './directives/lazyImage'

// Register ApexCharts
import VueApexCharts from 'vue3-apexcharts'

const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)
app.use(VueApexCharts)

// Register global directive
app.directive('lazy-image', lazyImageDirective)

app.mount('#app')
