/**
 * Composable for reliable order loading with retry logic
 * Ensures orders are always loaded, even in case of network issues
 */

import { ref, computed } from 'vue'
import { retryApiCall } from '@/utils/retry'
import ordersAPI from '@/api/orders'
import { useToast } from '@/composables/useToast'

export function useReliableOrders() {
  const orders = ref([])
  const loading = ref(false)
  const error = ref(null)
  const retryCount = ref(0)
  const lastRetryAt = ref(null)
  const isRetrying = ref(false)

  const { showToast } = useToast()

  /**
   * Load orders with automatic retry on failure
   * 
   * @param {Object} params - Query parameters for orders API
   * @param {Object} options - Retry options
   * @param {number} options.maxRetries - Maximum retries (default: 3)
   * @param {boolean} options.silent - Don't show toast notifications (default: false)
   * @param {boolean} options.showRetryProgress - Show retry progress toasts (default: true)
   */
  const loadOrders = async (params = {}, options = {}) => {
    const {
      maxRetries = 3,
      silent = false,
      showRetryProgress = true,
    } = options

    loading.value = true
    error.value = null
    retryCount.value = 0
    isRetrying.value = false

    try {
      const response = await retryApiCall(
        () => ordersAPI.list(params),
        {
          maxRetries,
          shouldRetry: (error) => {
            // Retry on network errors, 5xx, 429, 408
            if (!error.response) return true
            const status = error.response?.status
            return status === 408 || status === 429 || (status >= 500 && status < 600)
          },
          onRetry: (attempt, maxRetries, delay, error) => {
            retryCount.value = attempt
            lastRetryAt.value = new Date()
            isRetrying.value = true

            if (showRetryProgress && !silent) {
              const status = error.response?.status || 'network error'
              showToast(
                `Retrying order load (${attempt}/${maxRetries})... ${status}`,
                'warning',
                { duration: 2000 }
              )
            }
          },
        }
      )

      // Extract orders from response
      const data = response.data
      if (Array.isArray(data?.results)) {
        orders.value = data.results
      } else if (Array.isArray(data)) {
        orders.value = data
      } else {
        orders.value = []
      }

      // Reset retry state on success
      if (retryCount.value > 0 && !silent) {
        showToast(
          `Orders loaded successfully after ${retryCount.value} retry${retryCount.value > 1 ? 'ies' : ''}`,
          'success',
          { duration: 3000 }
        )
      }

      retryCount.value = 0
      isRetrying.value = false
      error.value = null

      return orders.value
    } catch (err) {
      error.value = err
      isRetrying.value = false

      // Show error toast if not silent
      if (!silent) {
        const errorMessage = err.response?.data?.detail || 
                           err.message || 
                           'Failed to load orders after multiple retries'
        showToast(errorMessage, 'error', { duration: 5000 })
      }

      // Return empty array instead of throwing
      orders.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Manually retry loading orders
   */
  const retry = async (params = {}, options = {}) => {
    return loadOrders(params, { ...options, silent: false })
  }

  /**
   * Refresh orders (same as load but with different messaging)
   */
  const refresh = async (params = {}, options = {}) => {
    return loadOrders(params, { ...options, silent: false })
  }

  /**
   * Check if we should show retry button
   */
  const shouldShowRetry = computed(() => {
    return error.value && !loading.value && !isRetrying.value
  })

  /**
   * Get retry status message
   */
  const retryStatus = computed(() => {
    if (isRetrying.value) {
      return `Retrying... (${retryCount.value}/${3})`
    }
    if (retryCount.value > 0) {
      return `Loaded after ${retryCount.value} retry${retryCount.value > 1 ? 'ies' : ''}`
    }
    return null
  })

  return {
    orders,
    loading,
    error,
    retryCount,
    lastRetryAt,
    isRetrying,
    shouldShowRetry,
    retryStatus,
    loadOrders,
    retry,
    refresh,
  }
}

