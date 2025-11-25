/**
 * Retry utility with exponential backoff
 * Provides configurable retry logic for API calls and other async operations
 */

/**
 * Sleep for a given number of milliseconds
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Retry an async function with exponential backoff
 * 
 * @param {Function} fn - The async function to retry
 * @param {Object} options - Retry options
 * @param {number} options.maxRetries - Maximum number of retries (default: 3)
 * @param {number} options.initialDelay - Initial delay in ms (default: 1000)
 * @param {number} options.maxDelay - Maximum delay in ms (default: 10000)
 * @param {number} options.multiplier - Backoff multiplier (default: 2)
 * @param {Function} options.shouldRetry - Function to determine if error should be retried (default: retry on network errors and 5xx)
 * @param {Function} options.onRetry - Callback called before each retry
 * @returns {Promise} The result of the function
 */
export async function retryWithBackoff(fn, options = {}) {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    multiplier = 2,
    shouldRetry = (error) => {
      // Default: retry on network errors and 5xx server errors
      if (!error.response) {
        return true // Network error
      }
      const status = error.response?.status
      return status >= 500 && status < 600 // Server errors
    },
    onRetry = null,
  } = options

  let lastError
  let delay = initialDelay

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error

      // Don't retry if we've exhausted retries or error shouldn't be retried
      if (attempt >= maxRetries || !shouldRetry(error)) {
        throw error
      }

      // Call onRetry callback if provided
      if (onRetry) {
        onRetry(attempt + 1, maxRetries, delay, error)
      }

      // Wait before retrying
      await sleep(delay)

      // Calculate next delay with exponential backoff
      delay = Math.min(delay * multiplier, maxDelay)
    }
  }

  throw lastError
}

/**
 * Retry an API call with exponential backoff
 * Specifically designed for axios requests
 * 
 * @param {Function} apiCall - Function that returns an axios promise
 * @param {Object} options - Retry options (same as retryWithBackoff)
 * @returns {Promise} The axios response
 */
export async function retryApiCall(apiCall, options = {}) {
  const defaultShouldRetry = (error) => {
    // Retry on:
    // - Network errors (no response)
    // - 5xx server errors
    // - 429 Too Many Requests (rate limiting)
    // - 408 Request Timeout
    if (!error.response) {
      return true // Network error
    }
    const status = error.response?.status
    return status === 408 || status === 429 || (status >= 500 && status < 600)
  }

  return retryWithBackoff(apiCall, {
    shouldRetry: defaultShouldRetry,
    ...options,
  })
}

/**
 * Create a retryable API call wrapper
 * Returns a function that can be called multiple times with automatic retry
 * 
 * @param {Function} apiCall - Function that returns an axios promise
 * @param {Object} options - Retry options
 * @returns {Function} Wrapped function with retry logic
 */
export function createRetryableApiCall(apiCall, options = {}) {
  return async (...args) => {
    return retryApiCall(() => apiCall(...args), options)
  }
}

/**
 * Check if error is retryable
 * 
 * @param {Error} error - The error to check
 * @returns {boolean} True if error should be retried
 */
export function isRetryableError(error) {
  if (!error.response) {
    return true // Network error
  }
  const status = error.response?.status
  return status === 408 || status === 429 || (status >= 500 && status < 600)
}

