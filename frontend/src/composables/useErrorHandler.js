import { useToast } from './useToast'
import { getErrorMessage, isNetworkError, isServerError, isClientError } from '@/utils/errorHandler'

/**
 * Enhanced error handler composable
 * Provides actionable error messages with guidance
 */
export function useErrorHandler() {
  const { error: showErrorToast, success: showSuccessToast, warning: showWarningToast } = useToast()

  /**
   * Show error with actionable guidance
   * @param {Error|Object|string} error - Error object or message
   * @param {Object} options - Options for error handling
   * @param {string} options.action - Action being performed (e.g., "saving order")
   * @param {string} options.title - Custom title for the error
   * @param {Function} options.onRetry - Retry function to call
   * @param {Function} options.onDismiss - Dismiss callback
   * @param {boolean} options.showToast - Whether to show toast notification (default: true)
   * @param {number} options.duration - Toast duration in ms
   * @returns {string} The error message that was displayed
   */
  const handleError = (error, options = {}) => {
    const {
      action = '',
      title = null,
      onRetry = null,
      onDismiss = null,
      showToast: shouldShowToast = true,
      duration = 7000
    } = options

    // Get user-friendly error message
    const message = getErrorMessage(error, 'An unexpected error occurred', action)

    // Don't show if message is null (suppressed error)
    if (!message) return null

    // Enhance message with actionable guidance
    const enhancedMessage = enhanceErrorMessage(message, error, options)

    if (shouldShowToast) {
      showErrorToast(enhancedMessage, duration)
    }

    return enhancedMessage
  }

  /**
   * Enhance error message with actionable guidance
   */
  const enhanceErrorMessage = (message, error, options) => {
    let enhanced = message

    // Add specific guidance based on error type
    if (isNetworkError(error)) {
      enhanced += ' If the problem persists, please check your internet connection or contact support.'
    } else if (isServerError(error)) {
      enhanced += ' Our team has been notified. Please try again in a few moments.'
    } else if (isClientError(error)) {
      const status = error?.response?.status
      if (status === 401) {
        enhanced += ' You will be redirected to the login page.'
      } else if (status === 403) {
        enhanced += ' If you believe this is an error, please contact your administrator.'
      } else if (status === 404) {
        enhanced += ' Please check the URL or return to the previous page.'
      } else if (status === 422) {
        enhanced += ' Please review the highlighted fields and correct any errors.'
      } else if (status === 429) {
        enhanced += ' Please wait a moment before trying again.'
      }
    }

    // Add retry suggestion if retry function is available
    if (options.onRetry) {
      enhanced += ' You can try again by clicking the retry button.'
    }

    return enhanced
  }

  /**
   * Handle error and show toast with retry option
   */
  const handleErrorWithRetry = (error, retryFn, action = '') => {
    return handleError(error, {
      action,
      onRetry: retryFn,
      duration: 10000 // Longer duration for retry option
    })
  }

  /**
   * Handle validation errors with field-specific guidance
   */
  const handleValidationError = (error, fields = {}) => {
    const message = getErrorMessage(error, 'Please check your input and try again.', 'Validation failed')
    
    // Extract field-specific errors if available
    if (error?.response?.data?.errors) {
      const fieldErrors = error.response.data.errors
      const fieldMessages = Object.keys(fieldErrors).map(field => {
        const fieldName = fields[field] || field.replace(/_/g, ' ')
        const errors = Array.isArray(fieldErrors[field]) 
          ? fieldErrors[field].join(', ')
          : fieldErrors[field]
        return `${fieldName}: ${errors}`
      })
      
      if (fieldMessages.length > 0) {
        return handleError(fieldMessages.join('. '), {
          action: 'Validation failed',
          duration: 8000
        })
      }
    }

    return handleError(message, {
      action: 'Validation failed',
      duration: 8000
    })
  }

  /**
   * Show success message
   */
  const handleSuccess = (message, duration = 5000) => {
    showSuccessToast(message, duration)
  }

  /**
   * Show warning message
   */
  const handleWarning = (message, duration = 6000) => {
    showWarningToast(message, duration)
  }

  return {
    handleError,
    handleErrorWithRetry,
    handleValidationError,
    handleSuccess,
    handleWarning,
    isNetworkError,
    isServerError,
    isClientError
  }
}

