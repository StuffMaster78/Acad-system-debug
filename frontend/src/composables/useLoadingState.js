import { ref, computed } from 'vue'

/**
 * Composable for managing loading states with minimum delay to prevent flickering
 * Only shows spinner if operation takes longer than minDelay (default 200ms)
 * 
 * @param {Object} options - Configuration options
 * @param {number} options.minDelay - Minimum delay in ms before showing spinner (default: 200)
 * @param {boolean} options.immediate - If true, show spinner immediately (default: false)
 * @returns {Object} Loading state management utilities
 */
export function useLoadingState(options = {}) {
  const { minDelay = 200, immediate = false } = options
  
  const isLoading = ref(false)
  const isActuallyLoading = ref(false) // Internal state that tracks actual loading
  let loadingTimeout = null
  let loadingStartTime = null

  /**
   * Start loading - will only show spinner after minDelay
   */
  const startLoading = () => {
    if (isActuallyLoading.value) {
      return // Already loading
    }
    
    isActuallyLoading.value = true
    loadingStartTime = Date.now()
    
    if (immediate) {
      isLoading.value = true
    } else {
      // Delay showing spinner
      loadingTimeout = setTimeout(() => {
        if (isActuallyLoading.value) {
          isLoading.value = true
        }
      }, minDelay)
    }
  }

  /**
   * Stop loading - clears spinner immediately
   */
  const stopLoading = () => {
    isActuallyLoading.value = false
    
    if (loadingTimeout) {
      clearTimeout(loadingTimeout)
      loadingTimeout = null
    }
    
    isLoading.value = false
    loadingStartTime = null
  }

  /**
   * Execute an async function with loading state management
   * Automatically handles start/stop and ensures cleanup
   * 
   * @param {Function} asyncFn - Async function to execute
   * @returns {Promise} Result of the async function
   */
  const withLoading = async (asyncFn) => {
    startLoading()
    try {
      const result = await asyncFn()
      return result
    } finally {
      stopLoading()
    }
  }

  /**
   * Reset loading state (useful for cleanup)
   */
  const reset = () => {
    stopLoading()
  }

  return {
    loading: computed(() => isLoading.value),
    isLoading: computed(() => isLoading.value),
    startLoading,
    stopLoading,
    withLoading,
    reset
  }
}

/**
 * Composable for managing multiple loading states
 * Useful for components that have multiple async operations
 * 
 * @param {Object} options - Configuration options
 * @param {number} options.minDelay - Minimum delay in ms before showing spinner (default: 200)
 * @returns {Object} Multiple loading state management utilities
 */
export function useMultipleLoadingStates(options = {}) {
  const { minDelay = 200 } = options
  
  const loadingStates = ref({})
  const loadingTimeouts = {}
  const loadingStartTimes = {}

  /**
   * Start loading for a specific key
   */
  const startLoading = (key) => {
    if (loadingStates.value[key]) {
      return // Already loading
    }
    
    loadingStartTimes[key] = Date.now()
    
    // Delay showing spinner
    loadingTimeouts[key] = setTimeout(() => {
      if (loadingStartTimes[key]) {
        loadingStates.value[key] = true
      }
    }, minDelay)
  }

  /**
   * Stop loading for a specific key
   */
  const stopLoading = (key) => {
    if (loadingTimeouts[key]) {
      clearTimeout(loadingTimeouts[key])
      delete loadingTimeouts[key]
    }
    
    delete loadingStartTimes[key]
    loadingStates.value[key] = false
  }

  /**
   * Check if a specific key is loading
   */
  const isLoading = (key) => {
    return loadingStates.value[key] === true
  }

  /**
   * Check if any key is loading
   */
  const isAnyLoading = computed(() => {
    return Object.values(loadingStates.value).some(state => state === true)
  })

  /**
   * Execute an async function with loading state for a specific key
   */
  const withLoading = async (key, asyncFn) => {
    startLoading(key)
    try {
      const result = await asyncFn()
      return result
    } finally {
      stopLoading(key)
    }
  }

  /**
   * Reset all loading states
   */
  const reset = () => {
    Object.keys(loadingTimeouts).forEach(key => {
      if (loadingTimeouts[key]) {
        clearTimeout(loadingTimeouts[key])
      }
    })
    Object.keys(loadingStates.value).forEach(key => {
      loadingStates.value[key] = false
    })
    Object.keys(loadingStartTimes).forEach(key => {
      delete loadingStartTimes[key]
    })
  }

  /**
   * Reset a specific loading state
   */
  const resetKey = (key) => {
    stopLoading(key)
  }

  return {
    loadingStates: computed(() => loadingStates.value),
    isLoading,
    isAnyLoading,
    startLoading,
    stopLoading,
    withLoading,
    reset,
    resetKey
  }
}

