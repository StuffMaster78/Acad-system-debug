import { computed, ref } from 'vue'

/**
 * Memoized computed property composable
 * Useful for expensive computations that depend on reactive values
 * 
 * @param {Function} fn - Computation function
 * @param {Array} deps - Dependency array (reactive refs/computed)
 * @returns {import('vue').ComputedRef} Memoized computed property
 */
export function useMemoized(fn, deps = []) {
  const cache = ref(new Map())
  const lastDeps = ref([])
  
  return computed(() => {
    // Create cache key from dependency values
    const depValues = deps.map(dep => {
      if (typeof dep === 'object' && dep !== null && 'value' in dep) {
        return dep.value
      }
      return dep
    })
    
    const cacheKey = JSON.stringify(depValues)
    
    // Check if dependencies changed
    const depsChanged = JSON.stringify(lastDeps.value) !== cacheKey
    
    if (depsChanged || !cache.value.has(cacheKey)) {
      const result = fn()
      cache.value.set(cacheKey, result)
      lastDeps.value = depValues
      return result
    }
    
    return cache.value.get(cacheKey)
  })
}

/**
 * Simple memoization helper for functions
 * @param {Function} fn - Function to memoize
 * @param {Function} keyFn - Function to generate cache key from arguments
 * @returns {Function} Memoized function
 */
export function memoize(fn, keyFn = (...args) => JSON.stringify(args)) {
  const cache = new Map()
  
  return function(...args) {
    const key = keyFn(...args)
    
    if (cache.has(key)) {
      return cache.get(key)
    }
    
    const result = fn(...args)
    cache.set(key, result)
    return result
  }
}

