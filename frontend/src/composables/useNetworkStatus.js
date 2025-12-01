/**
 * Network status composable
 * Monitors network connectivity and provides status information
 */
import { ref, onMounted, onUnmounted } from 'vue'

export function useNetworkStatus() {
  const isOnline = ref(navigator.onLine)
  const wasOffline = ref(false)

  const updateOnlineStatus = () => {
    isOnline.value = navigator.onLine
    
    if (!isOnline.value) {
      wasOffline.value = true
    } else if (wasOffline.value) {
      // Just came back online
      wasOffline.value = false
      // Could trigger a refresh here if needed
    }
  }

  onMounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
  })

  onUnmounted(() => {
    window.removeEventListener('online', updateOnlineStatus)
    window.removeEventListener('offline', updateOnlineStatus)
  })

  return {
    isOnline,
    wasOffline,
  }
}

