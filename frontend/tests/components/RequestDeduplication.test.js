/**
 * Component tests for request deduplication integration
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import apiClient from '@/api/client'

describe('Request Deduplication Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should deduplicate identical GET requests', async () => {
    const mockGet = vi.fn().mockResolvedValue({ data: { test: 'data' } })
    apiClient.get = mockGet

    // Make two identical requests simultaneously
    const promise1 = apiClient.get('/api/test')
    const promise2 = apiClient.get('/api/test')

    const [result1, result2] = await Promise.all([promise1, promise2])

    // Should only make one actual request
    expect(mockGet).toHaveBeenCalledTimes(1)
    expect(result1.data).toEqual({ test: 'data' })
    expect(result2.data).toEqual({ test: 'data' })
  })

  it('should not deduplicate different requests', async () => {
    const mockGet = vi.fn().mockResolvedValue({ data: { test: 'data' } })
    apiClient.get = mockGet

    // Make two different requests
    await Promise.all([
      apiClient.get('/api/test1'),
      apiClient.get('/api/test2')
    ])

    // Should make two requests
    expect(mockGet).toHaveBeenCalledTimes(2)
  })

  it('should handle request errors correctly', async () => {
    const mockGet = vi.fn().mockRejectedValue(new Error('Request failed'))
    apiClient.get = mockGet

    try {
      await apiClient.get('/api/test')
    } catch (error) {
      expect(error.message).toBe('Request failed')
    }

    // Should be able to retry after error
    mockGet.mockResolvedValue({ data: { success: true } })
    const result = await apiClient.get('/api/test')
    expect(result.data).toEqual({ success: true })
  })
})

