/**
 * Composable for detecting connection status and auto-retrying on reconnect
 */

import { ref, onMounted, onUnmounted } from 'vue'

export function useConnectionStatus() {
  const isOnline = ref(navigator.onLine)
  const wasOffline = ref(false)

  const updateOnlineStatus = () => {
    const nowOnline = navigator.onLine
    if (!isOnline.value && nowOnline) {
      // Just came back online
      wasOffline.value = true
      // Trigger a custom event that components can listen to
      window.dispatchEvent(new CustomEvent('connection-restored'))
    }
    isOnline.value = nowOnline
  }

  onMounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
    
    // Also check periodically (every 5 seconds) for cases where events don't fire
    const checkInterval = setInterval(() => {
      const currentStatus = navigator.onLine
      if (currentStatus !== isOnline.value) {
        updateOnlineStatus()
      }
    }, 5000)

    // Store interval ID for cleanup
    window._connectionCheckInterval = checkInterval
  })

  onUnmounted(() => {
    window.removeEventListener('online', updateOnlineStatus)
    window.removeEventListener('offline', updateOnlineStatus)
    
    if (window._connectionCheckInterval) {
      clearInterval(window._connectionCheckInterval)
      delete window._connectionCheckInterval
    }
  })

  return {
    isOnline,
    wasOffline,
  }
}

