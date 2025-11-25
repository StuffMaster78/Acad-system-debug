/**
 * Error handling utilities
 * Provides consistent error message extraction and formatting
 */

/**
 * Humanize field names for better error messages
 * @param {string} field - Field name (e.g., "email_address" or "first_name")
 * @returns {string} Humanized field name (e.g., "Email address" or "First name")
 */
function humanizeFieldName(field) {
  return field
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Extract user-friendly error message from error object
 * @param {Error|Object} error - Error object from API call
 * @param {string} defaultMessage - Default message if error extraction fails
 * @param {string} action - Action being performed (e.g., "saving order", "loading data")
 * @returns {string} User-friendly error message
 */
export function getErrorMessage(error, defaultMessage = 'An unexpected error occurred', action = '') {
  if (!error) return defaultMessage

  // Handle axios/API errors
  if (error.response) {
    const data = error.response.data
    const status = error.response.status

    // Check for detail field (DRF standard) - most common
    if (data?.detail) {
      const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      // Add action context if provided
      return action ? `${action}: ${detail}` : detail
    }

    // Check for message field
    if (data?.message) {
      return action ? `${action}: ${data.message}` : data.message
    }

    // Check for error field
    if (data?.error) {
      const errorMsg = typeof data.error === 'string' ? data.error : JSON.stringify(data.error)
      return action ? `${action}: ${errorMsg}` : errorMsg
    }

    // Check for errors object (validation errors) - format nicely
    if (data?.errors) {
      const errorMessages = []
      if (typeof data.errors === 'object') {
        Object.keys(data.errors).forEach(key => {
          const value = data.errors[key]
          const fieldName = humanizeFieldName(key)
          
          if (Array.isArray(value)) {
            // Join array errors with "and" for better readability
            const errors = value.filter(e => e).join(' and ')
            if (errors) {
              errorMessages.push(`${fieldName}: ${errors}`)
            }
          } else if (typeof value === 'string' && value) {
            errorMessages.push(`${fieldName}: ${value}`)
          } else if (typeof value === 'object') {
            // Handle nested errors
            const nestedErrors = Object.keys(value).map(nestedKey => {
              const nestedValue = value[nestedKey]
              if (Array.isArray(nestedValue)) {
                return nestedValue.join(' and ')
              }
              return nestedValue
            }).join(', ')
            if (nestedErrors) {
              errorMessages.push(`${fieldName} (${nestedErrors})`)
            }
          }
        })
      }
      if (errorMessages.length > 0) {
        const formatted = errorMessages.length === 1 
          ? errorMessages[0]
          : errorMessages.join('. ')
        return action ? `${action}: ${formatted}` : formatted
      }
    }

    // Check for non_field_errors (DRF validation)
    if (data?.non_field_errors) {
      const nonFieldErrors = Array.isArray(data.non_field_errors)
        ? data.non_field_errors.join('. ')
        : data.non_field_errors
      return action ? `${action}: ${nonFieldErrors}` : nonFieldErrors
    }

    // HTTP status-based messages with actionable guidance
    const statusMessages = {
      400: 'Invalid request. Please check your input and try again.',
      401: 'Your session has expired. Please log in again to continue.',
      403: 'You don\'t have permission to perform this action. If you believe this is an error, please contact support.',
      404: 'The requested item could not be found. It may have been deleted or moved.',
      409: 'This action conflicts with the current state. Please refresh the page and try again.',
      422: 'Please check your input and correct any errors before submitting.',
      429: 'Too many requests. Please wait a moment and try again.',
      500: 'A server error occurred. Our team has been notified. Please try again in a few moments.',
      502: 'Service temporarily unavailable. Please try again in a few moments.',
      503: 'Service temporarily unavailable. Please try again in a few moments.',
    }

    if (statusMessages[status]) {
      return action ? `${action}: ${statusMessages[status]}` : statusMessages[status]
    }
  }

  // Handle network errors with actionable guidance
  if (error.message) {
    if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
      return 'Unable to connect to the server. Please check your internet connection and try again.'
    }
    if (error.message.includes('timeout')) {
      return 'The request took too long. Please check your connection and try again.'
    }
    // Return the error message but make it more user-friendly if it's technical
    if (error.message.includes('ECONNREFUSED') || error.message.includes('ERR_')) {
      return 'Connection error. Please check your internet connection and try again.'
    }
    return action ? `${action}: ${error.message}` : error.message
  }

  // Fallback with action context
  return action ? `${action}: ${defaultMessage}` : defaultMessage
}

/**
 * Format error for display with context
 * @param {Error|Object} error - Error object
 * @param {string} context - Context of the error (e.g., "loading orders")
 * @returns {string} Formatted error message
 */
export function formatError(error, context = '') {
  return getErrorMessage(error, 'An unexpected error occurred', context)
}

/**
 * Get success message for common actions
 * @param {string} action - Action performed (e.g., "save", "delete", "update")
 * @param {string} item - Item name (e.g., "order", "message", "profile")
 * @returns {string} Success message
 */
export function getSuccessMessage(action, item = 'item') {
  const messages = {
    save: `${item.charAt(0).toUpperCase() + item.slice(1)} saved successfully!`,
    create: `${item.charAt(0).toUpperCase() + item.slice(1)} created successfully!`,
    update: `${item.charAt(0).toUpperCase() + item.slice(1)} updated successfully!`,
    delete: `${item.charAt(0).toUpperCase() + item.slice(1)} deleted successfully!`,
    submit: `${item.charAt(0).toUpperCase() + item.slice(1)} submitted successfully!`,
    cancel: `${item.charAt(0).toUpperCase() + item.slice(1)} cancelled successfully!`,
    complete: `${item.charAt(0).toUpperCase() + item.slice(1)} completed successfully!`,
    send: `${item.charAt(0).toUpperCase() + item.slice(1)} sent successfully!`,
    upload: `${item.charAt(0).toUpperCase() + item.slice(1)} uploaded successfully!`,
    download: `${item.charAt(0).toUpperCase() + item.slice(1)} downloaded successfully!`,
  }
  
  return messages[action] || `${item.charAt(0).toUpperCase() + item.slice(1)} ${action} completed successfully!`
}

/**
 * Check if error is a network error
 * @param {Error|Object} error - Error object
 * @returns {boolean}
 */
export function isNetworkError(error) {
  if (!error) return false
  if (error.message?.includes('Network Error') || error.message?.includes('Failed to fetch')) {
    return true
  }
  if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED') {
    return true
  }
  return false
}

/**
 * Check if error is a server error (5xx)
 * @param {Error|Object} error - Error object
 * @returns {boolean}
 */
export function isServerError(error) {
  if (!error?.response) return false
  const status = error.response.status
  return status >= 500 && status < 600
}

/**
 * Check if error is a client error (4xx)
 * @param {Error|Object} error - Error object
 * @returns {boolean}
 */
export function isClientError(error) {
  if (!error?.response) return false
  const status = error.response.status
  return status >= 400 && status < 500
}

