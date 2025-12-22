import { ref, watch, onUnmounted } from 'vue'

/**
 * Debounce utility function
 * Delays function execution until after a specified wait time
 * 
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @param {boolean} immediate - If true, execute immediately on first call
 * @returns {Function} Debounced function
 */
export function debounce(func, wait = 300, immediate = false) {
  let timeout = null
  
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    
    const callNow = immediate && !timeout
    
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    
    if (callNow) func(...args)
  }
}

/**
 * Vue composable for debounced values
 * Useful for search inputs and form fields
 * 
 * @param {import('vue').Ref} value - Reactive value to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {import('vue').Ref} Debounced value
 */
export function useDebounce(value, delay = 300) {
  const debouncedValue = ref(value.value)
  let timeout = null
  
  watch(value, (newValue) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      debouncedValue.value = newValue
    }, delay)
  })
  
  onUnmounted(() => {
    clearTimeout(timeout)
  })
  
  return debouncedValue
}
