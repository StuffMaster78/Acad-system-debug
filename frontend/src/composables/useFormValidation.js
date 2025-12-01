/**
 * Form validation composable
 * Provides consistent form validation patterns across the application
 */
import { ref, computed } from 'vue'
import { getErrorMessage } from '@/utils/errorHandler'

export function useFormValidation(initialErrors = {}) {
  const errors = ref({ ...initialErrors })
  const touched = ref({})
  const submitting = ref(false)

  /**
   * Set error for a specific field
   */
  const setError = (field, message) => {
    errors.value[field] = message
    touched.value[field] = true
  }

  /**
   * Set multiple errors at once (from API response)
   */
  const setErrors = (errorObject) => {
    if (errorObject && typeof errorObject === 'object') {
      Object.keys(errorObject).forEach(key => {
        const value = errorObject[key]
        if (Array.isArray(value)) {
          errors.value[key] = value[0] // Take first error message
        } else if (typeof value === 'string') {
          errors.value[key] = value
        }
        touched.value[key] = true
      })
    }
  }

  /**
   * Clear error for a specific field
   */
  const clearError = (field) => {
    delete errors.value[field]
  }

  /**
   * Clear all errors
   */
  const clearAllErrors = () => {
    errors.value = {}
    touched.value = {}
  }

  /**
   * Mark field as touched
   */
  const touchField = (field) => {
    touched.value[field] = true
  }

  /**
   * Check if field has error
   */
  const hasError = (field) => {
    return !!errors.value[field]
  }

  /**
   * Get error message for field
   */
  const getError = (field) => {
    return errors.value[field] || null
  }

  /**
   * Check if field has been touched
   */
  const isTouched = (field) => {
    return !!touched.value[field]
  }

  /**
   * Check if form has any errors
   */
  const hasErrors = computed(() => {
    return Object.keys(errors.value).length > 0
  })

  /**
   * Check if form is valid (no errors)
   */
  const isValid = computed(() => {
    return !hasErrors.value
  })

  /**
   * Handle API error response
   */
  const handleApiError = (error, fieldMap = {}) => {
    // Clear previous errors
    clearAllErrors()
    
    if (error.response?.data) {
      const data = error.response.data
      
      // Map API field names to form field names if needed
      Object.keys(data).forEach(apiField => {
        const formField = fieldMap[apiField] || apiField
        setError(formField, Array.isArray(data[apiField]) 
          ? data[apiField][0] 
          : data[apiField])
      })
      
      // Handle non-field errors
      if (data.detail && !data.detail.match(/^\w+:/)) {
        setError('_general', data.detail)
      } else if (data.message) {
        setError('_general', data.message)
      } else if (data.error) {
        setError('_general', data.error)
      }
    } else {
      // Network or other errors
      const message = getErrorMessage(error, 'An error occurred')
      setError('_general', message)
    }
  }

  /**
   * Validate required field
   */
  const validateRequired = (value, fieldName, customMessage = null) => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      setError(fieldName, customMessage || `${fieldName} is required`)
      return false
    }
    clearError(fieldName)
    return true
  }

  /**
   * Validate email
   */
  const validateEmail = (value, fieldName = 'email') => {
    if (!value) {
      setError(fieldName, 'Email is required')
      return false
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      setError(fieldName, 'Please enter a valid email address')
      return false
    }
    
    clearError(fieldName)
    return true
  }

  /**
   * Validate minimum length
   */
  const validateMinLength = (value, minLength, fieldName, customMessage = null) => {
    if (!value || value.length < minLength) {
      setError(fieldName, customMessage || `${fieldName} must be at least ${minLength} characters`)
      return false
    }
    clearError(fieldName)
    return true
  }

  /**
   * Validate maximum length
   */
  const validateMaxLength = (value, maxLength, fieldName, customMessage = null) => {
    if (value && value.length > maxLength) {
      setError(fieldName, customMessage || `${fieldName} must be no more than ${maxLength} characters`)
      return false
    }
    clearError(fieldName)
    return true
  }

  /**
   * Validate number range
   */
  const validateNumberRange = (value, min, max, fieldName) => {
    const num = Number(value)
    if (isNaN(num)) {
      setError(fieldName, `${fieldName} must be a number`)
      return false
    }
    if (num < min || num > max) {
      setError(fieldName, `${fieldName} must be between ${min} and ${max}`)
      return false
    }
    clearError(fieldName)
    return true
  }

  /**
   * Validate date is in future
   */
  const validateFutureDate = (value, fieldName) => {
    if (!value) {
      setError(fieldName, `${fieldName} is required`)
      return false
    }
    
    const date = new Date(value)
    const now = new Date()
    
    if (date <= now) {
      setError(fieldName, `${fieldName} must be in the future`)
      return false
    }
    
    clearError(fieldName)
    return true
  }

  /**
   * Validate passwords match
   */
  const validatePasswordMatch = (password, confirmPassword, fieldName = 'password_confirm') => {
    if (password !== confirmPassword) {
      setError(fieldName, 'Passwords do not match')
      return false
    }
    clearError(fieldName)
    return true
  }

  return {
    // State
    errors,
    touched,
    submitting,
    
    // Computed
    hasErrors,
    isValid,
    
    // Methods
    setError,
    setErrors,
    clearError,
    clearAllErrors,
    touchField,
    hasError,
    getError,
    isTouched,
    handleApiError,
    
    // Validators
    validateRequired,
    validateEmail,
    validateMinLength,
    validateMaxLength,
    validateNumberRange,
    validateFutureDate,
    validatePasswordMatch,
  }
}

