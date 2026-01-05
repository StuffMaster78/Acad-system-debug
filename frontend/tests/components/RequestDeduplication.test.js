/**
 * Component tests for request deduplication integration
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import apiClient from '@/api/client'
import { deduplicateRequest, clearInFlightRequests } from '@/utils/requestDeduplication'

describe('Request Deduplication Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    clearInFlightRequests() // Clear any in-flight requests between tests
  })

  it('should deduplicate identical GET requests', async () => {
    // Create a mock request function that tracks calls
    // The deduplicateRequest function calls requestFn with config, so we need to accept it
    const requestFn = vi.fn((config) => {
      return Promise.resolve({ data: { test: 'data' } })
    })
    
    // Make two identical requests using the deduplication utility
    const config = { method: 'get', url: '/api/test' }
    
    // Call deduplicateRequest with the same config - should deduplicate
    // Store the first promise before calling the second time
    const promise1 = deduplicateRequest(requestFn, config)
    
    // Use Promise.resolve() to yield to the event loop, ensuring the first promise is stored
    await Promise.resolve()
    
    // Second call should return the same promise (deduplicated)
    const promise2 = deduplicateRequest(requestFn, config)
    
    // Both should be the same promise (deduplicated)
    expect(promise1).toBe(promise2)
    
    // Wait for both to resolve
    const [result1, result2] = await Promise.all([promise1, promise2])
    
    // Request function should only be called once (deduplication working)
    expect(requestFn).toHaveBeenCalledTimes(1)
    expect(result1.data).toEqual({ test: 'data' })
    expect(result2.data).toEqual({ test: 'data' })
  })

  it('should not deduplicate different requests', async () => {
    // Create a mock request function that tracks calls
    const requestFn = vi.fn((config) => {
      return Promise.resolve({ data: { test: 'data', url: config.url } })
    })
    
    // Make two different requests
    const config1 = { method: 'get', url: '/api/test1' }
    const config2 = { method: 'get', url: '/api/test2' }
    const promise1 = deduplicateRequest(() => requestFn(config1), config1)
    const promise2 = deduplicateRequest(() => requestFn(config2), config2)
    
    // Wait for both to resolve
    await Promise.all([promise1, promise2])
    
    // Should make two requests (different URLs)
    expect(requestFn).toHaveBeenCalledTimes(2)
  })

  it('should handle request errors correctly', async () => {
    // Create a mock request function that fails first, then succeeds
    let callCount = 0
    const requestFn = vi.fn(() => {
      callCount++
      if (callCount === 1) {
        return Promise.reject(new Error('Request failed'))
      }
      return Promise.resolve({ data: { success: true } })
    })
    
    const config = { method: 'get', url: '/api/test' }
    
    // First request should fail
    try {
      await deduplicateRequest(requestFn, config)
      expect.fail('Should have thrown an error')
    } catch (error) {
      expect(error.message).toBe('Request failed')
    }
    
    // Second request (after error cleared) should succeed
    const result = await deduplicateRequest(requestFn, config)
    expect(result.data).toEqual({ success: true })
    expect(requestFn).toHaveBeenCalledTimes(2)
  })
})

