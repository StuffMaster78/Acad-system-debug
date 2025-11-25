import { ref, onMounted, onUnmounted } from 'vue'
import onlineStatusAPI from '@/api/online-status'

/**
 * Composable for managing online status updates
 * Automatically updates user's online status periodically
 */
export function useOnlineStatus(intervalMs = 30000) {
  const isUpdating = ref(false)
  let updateInterval = null

  const updateStatus = async () => {
    if (isUpdating.value) return
    
    try {
      isUpdating.value = true
      await onlineStatusAPI.updateStatus()
    } catch (error) {
      console.error('Failed to update online status:', error)
    } finally {
      isUpdating.value = false
    }
  }

  const start = () => {
    // Update immediately
    updateStatus()
    
    // Then update periodically
    updateInterval = setInterval(updateStatus, intervalMs)
  }

  const stop = () => {
    if (updateInterval) {
      clearInterval(updateInterval)
      updateInterval = null
    }
  }

  onMounted(() => {
    start()
  })

  onUnmounted(() => {
    stop()
  })

  return {
    updateStatus,
    start,
    stop,
    isUpdating
  }
}

