/**
 * Request Deduplication Utility
 * Prevents multiple identical API requests from being made simultaneously
 * Returns the same promise for duplicate requests
 */

// Map to track in-flight requests
const inFlightRequests = new Map()

/**
 * Generate a unique key for a request
 */
function getRequestKey(config) {
  const { method = 'get', url, params, data } = config
  
  // Create a stable key from request details
  const keyParts = [
    method.toUpperCase(),
    url,
    params ? JSON.stringify(params) : '',
    data ? JSON.stringify(data) : ''
  ]
  
  return keyParts.join('|')
}

/**
 * Deduplicate API requests
 * If an identical request is already in flight, return the same promise
 * 
 * @param {Function} requestFn - The function that makes the API request
 * @param {Object} config - Axios request config
 * @returns {Promise} The request promise (shared if duplicate)
 */
export function deduplicateRequest(requestFn, config) {
  const key = getRequestKey(config)
  
  // If request is already in flight, return the existing promise
  if (inFlightRequests.has(key)) {
    if (import.meta.env.DEV) {
      console.debug(`[Request Deduplication] Reusing in-flight request: ${key}`)
    }
    return inFlightRequests.get(key)
  }
  
  // Create new request promise
  const requestPromise = requestFn(config)
    .then((response) => {
      // Remove from in-flight requests on success
      inFlightRequests.delete(key)
      return response
    })
    .catch((error) => {
      // Remove from in-flight requests on error
      inFlightRequests.delete(key)
      throw error
    })
  
  // Store the promise
  inFlightRequests.set(key, requestPromise)
  
  if (import.meta.env.DEV) {
    console.debug(`[Request Deduplication] New request: ${key}`)
  }
  
  return requestPromise
}

/**
 * Clear all in-flight requests (useful for testing or cleanup)
 */
export function clearInFlightRequests() {
  inFlightRequests.clear()
}

/**
 * Get count of in-flight requests
 */
export function getInFlightRequestCount() {
  return inFlightRequests.size
}

/**
 * Get all in-flight request keys (for debugging)
 */
export function getInFlightRequestKeys() {
  return Array.from(inFlightRequests.keys())
}

