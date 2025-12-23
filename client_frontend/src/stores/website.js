import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

export const useWebsiteStore = defineStore('website', () => {
  const website = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const themeColor = computed(() => website.value?.theme_color || '#0ea5e9')
  const logo = computed(() => website.value?.logo)
  const siteName = computed(() => website.value?.name || 'Writing Services')

  // Detect website from domain
  async function detectWebsite() {
    loading.value = true
    error.value = null
    
    try {
      const domain = window.location.origin
      const response = await apiClient.get('/websites/websites/', {
        params: { domain }
      })
      
      // Handle both single object and array response
      if (Array.isArray(response.data)) {
        website.value = response.data[0] || null
      } else if (response.data?.results) {
        website.value = response.data.results[0] || null
      } else {
        website.value = response.data || null
      }
      
      // Apply theme color if available
      if (website.value?.theme_color) {
        document.documentElement.style.setProperty('--primary-color', website.value.theme_color)
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load website'
      console.error('Website detection error:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    website,
    loading,
    error,
    themeColor,
    logo,
    siteName,
    detectWebsite,
  }
})

