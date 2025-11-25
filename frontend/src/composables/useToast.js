import { ref } from 'vue'

/**
 * Toast notification system
 * Provides a composable for showing toast notifications throughout the app
 */

const toasts = ref([])
let toastIdCounter = 0

export function useToast() {
  const showToast = (message, type = 'info', duration = 5000) => {
    const id = ++toastIdCounter
    const toast = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      duration,
      visible: true,
    }

    toasts.value.push(toast)

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      // Fade out animation
      toasts.value[index].visible = false
      setTimeout(() => {
        toasts.value.splice(index, 1)
      }, 300) // Match CSS transition duration
    }
  }

  const success = (message, duration = 5000) => {
    return showToast(message, 'success', duration)
  }

  const error = (message, duration = 7000) => {
    return showToast(message, 'error', duration)
  }

  const warning = (message, duration = 6000) => {
    return showToast(message, 'warning', duration)
  }

  const info = (message, duration = 5000) => {
    return showToast(message, 'info', duration)
  }

  const clearAll = () => {
    toasts.value.forEach(toast => {
      toast.visible = false
    })
    setTimeout(() => {
      toasts.value = []
    }, 300)
  }

  return {
    toasts,
    showToast,
    removeToast,
    success,
    error,
    warning,
    info,
    clearAll,
  }
}

