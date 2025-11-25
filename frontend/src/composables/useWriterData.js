import { ref } from 'vue'
import writerDashboardAPI from '@/api/writer-dashboard'

/**
 * Composable for consistent writer data fetching with error handling and retry logic
 */
export function useWriterData() {
  const loading = ref(false)
  const error = ref(null)
  const lastFetched = ref(null)

  const fetchWithRetry = async (fetchFn, retries = 2, delay = 1000) => {
    for (let i = 0; i <= retries; i++) {
      try {
        error.value = null
        const result = await fetchFn()
        lastFetched.value = new Date()
        return result
      } catch (err) {
        error.value = err
        console.error(`Fetch attempt ${i + 1} failed:`, err)
        
        if (i < retries) {
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
        } else {
          // Last attempt failed
          throw err
        }
      }
    }
  }

  const handleError = (err, defaultMessage = 'An error occurred') => {
    const message = err.response?.data?.detail || 
                   err.response?.data?.message || 
                   err.message || 
                   defaultMessage
    
    error.value = {
      message,
      status: err.response?.status,
      data: err.response?.data,
    }
    
    return message
  }

  const clearError = () => {
    error.value = null
  }

  return {
    loading,
    error,
    lastFetched,
    fetchWithRetry,
    handleError,
    clearError,
  }
}

/**
 * Composable for auto-refreshing data
 */
export function useAutoRefresh(fetchFn, intervalMs = 30000) {
  const { loading, error, fetchWithRetry, handleError } = useWriterData()
  let refreshInterval = null

  const startAutoRefresh = () => {
    if (refreshInterval) return
    
    refreshInterval = setInterval(async () => {
      if (!loading.value) {
        try {
          await fetchWithRetry(fetchFn)
        } catch (err) {
          handleError(err, 'Auto-refresh failed')
        }
      }
    }, intervalMs)
  }

  const stopAutoRefresh = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }

  return {
    loading,
    error,
    startAutoRefresh,
    stopAutoRefresh,
  }
}

