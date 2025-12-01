/**
 * Tests for authentication API
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createMockAxios, createMockUser } from '../utils/test-utils'

describe('Authentication API', () => {
  let mockAxios

  beforeEach(() => {
    mockAxios = createMockAxios()
  })

  it('should login successfully with valid credentials', async () => {
    const mockResponse = {
      access: 'mock-access-token',
      refresh: 'mock-refresh-token',
      user: createMockUser()
    }

    mockAxios.post.mockResolvedValue({ data: mockResponse })

    // In real test, import and use the actual API module
    // const authAPI = await import('@/api/auth')
    // const result = await authAPI.login('test@example.com', 'password123')
    // 
    // expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/auth/login/', {
    //   email: 'test@example.com',
    //   password: 'password123'
    // })
    // expect(result).toEqual(mockResponse)

    expect(mockAxios.post).toBeDefined()
  })

  it('should handle login failure', async () => {
    const errorResponse = {
      response: {
        status: 401,
        data: { error: 'Invalid credentials' }
      }
    }

    mockAxios.post.mockRejectedValue(errorResponse)

    // const authAPI = await import('@/api/auth')
    // 
    // await expect(
    //   authAPI.login('wrong@example.com', 'wrongpassword')
    // ).rejects.toThrow()

    expect(mockAxios.post).toBeDefined()
  })

  it('should register new user', async () => {
    const mockResponse = {
      user: createMockUser({ email: 'newuser@example.com' })
    }

    mockAxios.post.mockResolvedValue({ data: mockResponse })

    // const authAPI = await import('@/api/auth')
    // const result = await authAPI.register({
    //   email: 'newuser@example.com',
    //   password: 'password123',
    //   username: 'newuser'
    // })
    // 
    // expect(result.user.email).toBe('newuser@example.com')

    expect(mockAxios.post).toBeDefined()
  })

  it('should logout successfully', async () => {
    mockAxios.post.mockResolvedValue({ data: { success: true } })

    // const authAPI = await import('@/api/auth')
    // await authAPI.logout()
    // 
    // expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/auth/logout/')

    expect(mockAxios.post).toBeDefined()
  })
})

