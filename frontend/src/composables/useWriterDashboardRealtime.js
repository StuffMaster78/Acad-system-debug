import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Opens an SSE connection to the writer dashboard realtime stream and exposes connection status.
 * @param {Object} options
 * @param {(payload: Object) => void} [options.onMessage] callback when payload arrives
 * @param {number} [options.retryBaseDelay=2000] base reconnect delay in ms
 */
export function useWriterDashboardRealtime(options = {}) {
  const { onMessage, retryBaseDelay = 2000 } = options
  const status = ref('idle')
  const lastEventAt = ref(null)
  const retryCount = ref(0)

  let eventSource = null
  let reconnectTimer = null

  const cleanup = () => {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  const scheduleReconnect = () => {
    if (reconnectTimer) return
    const delay = Math.min(30000, retryBaseDelay * Math.max(1, retryCount.value + 1))
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      retryCount.value += 1
      connect()
    }, delay)
  }

  const connect = () => {
    cleanup()
    status.value = 'connecting'

    eventSource = new EventSource('/writer-management/dashboard/realtime/stream/')

    eventSource.addEventListener('writer_dashboard', (event) => {
      try {
        const payload = JSON.parse(event.data || '{}')
        lastEventAt.value = new Date()
        if (typeof onMessage === 'function') {
          onMessage(payload)
        }
      } catch (error) {
        console.error('Failed to parse realtime dashboard payload', error)
      }
    })

    eventSource.onopen = () => {
      status.value = 'connected'
      retryCount.value = 0
    }

    eventSource.onerror = () => {
      status.value = 'disconnected'
      cleanup()
      scheduleReconnect()
    }
  }

  onMounted(connect)
  onUnmounted(cleanup)

  return {
    status,
    lastEventAt,
    retryCount,
    reconnect: connect,
    disconnect: cleanup,
  }
}

