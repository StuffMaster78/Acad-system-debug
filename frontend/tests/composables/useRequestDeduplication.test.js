/**
 * Tests for request deduplication utility
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { deduplicateRequest, clearInFlightRequests } from '@/utils/requestDeduplication'

describe('Request Deduplication', () => {
  beforeEach(() => {
    clearInFlightRequests()
  })

  it('should make a new request when no duplicate exists', async () => {
    const mockRequest = vi.fn().mockResolvedValue({ data: 'test' })
    const config = { method: 'get', url: '/api/test', params: {} }

    const result = await deduplicateRequest(mockRequest, config)

    expect(mockRequest).toHaveBeenCalledTimes(1)
    expect(result).toEqual({ data: 'test' })
  })

  it('should reuse in-flight request for duplicates', async () => {
    const mockRequest = vi.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: 'test' }), 100))
    )
    const config = { method: 'get', url: '/api/test', params: {} }

    // Start two identical requests
    const promise1 = deduplicateRequest(mockRequest, config)
    const promise2 = deduplicateRequest(mockRequest, config)

    const [result1, result2] = await Promise.all([promise1, promise2])

    // Should only call the request function once
    expect(mockRequest).toHaveBeenCalledTimes(1)
    expect(result1).toEqual({ data: 'test' })
    expect(result2).toEqual({ data: 'test' })
  })

  it('should handle different requests separately', async () => {
    const mockRequest = vi.fn().mockResolvedValue({ data: 'test' })
    const config1 = { method: 'get', url: '/api/test1', params: {} }
    const config2 = { method: 'get', url: '/api/test2', params: {} }

    await Promise.all([
      deduplicateRequest(mockRequest, config1),
      deduplicateRequest(mockRequest, config2)
    ])

    expect(mockRequest).toHaveBeenCalledTimes(2)
  })

  it('should clear in-flight requests on error', async () => {
    const mockRequest = vi.fn().mockRejectedValue(new Error('Request failed'))
    const config = { method: 'get', url: '/api/test', params: {} }

    try {
      await deduplicateRequest(mockRequest, config)
    } catch (error) {
      expect(error.message).toBe('Request failed')
    }

    // Should be able to make a new request after error
    mockRequest.mockResolvedValue({ data: 'success' })
    const result = await deduplicateRequest(mockRequest, config)
    expect(result).toEqual({ data: 'success' })
  })

  it('should generate unique keys for different params', async () => {
    const mockRequest = vi.fn().mockResolvedValue({ data: 'test' })
    const config1 = { method: 'get', url: '/api/test', params: { page: 1 } }
    const config2 = { method: 'get', url: '/api/test', params: { page: 2 } }

    await Promise.all([
      deduplicateRequest(mockRequest, config1),
      deduplicateRequest(mockRequest, config2)
    ])

    expect(mockRequest).toHaveBeenCalledTimes(2)
  })
})

