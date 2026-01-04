/**
 * API mocking utilities for frontend tests
 */
import { vi } from 'vitest'
import axios from 'axios'

/**
 * Mock axios instance for testing
 */
export const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    request: { use: vi.fn(), eject: vi.fn() },
    response: { use: vi.fn(), eject: vi.fn() }
  }
}

/**
 * Create a mock API response
 */
export function createMockResponse(data, status = 200, statusText = 'OK') {
  return {
    data,
    status,
    statusText,
    headers: {},
    config: {}
  }
}

/**
 * Create a mock API error
 */
export function createMockError(message, status = 400, data = null) {
  const error = new Error(message)
  error.response = {
    data: data || { error: message },
    status,
    statusText: 'Bad Request',
    headers: {}
  }
  return error
}

/**
 * Mock successful API call
 */
export function mockApiSuccess(method, url, responseData) {
  mockApiClient[method].mockResolvedValueOnce(createMockResponse(responseData))
}

/**
 * Mock failed API call
 */
export function mockApiError(method, url, errorMessage, status = 400) {
  mockApiClient[method].mockRejectedValueOnce(createMockError(errorMessage, status))
}

/**
 * Reset all API mocks
 */
export function resetApiMocks() {
  Object.keys(mockApiClient).forEach(key => {
    if (typeof mockApiClient[key] === 'function' && key !== 'interceptors') {
      mockApiClient[key].mockReset()
    }
  })
}

/**
 * Mock localStorage
 */
export function mockLocalStorage() {
  const store = {}
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => { store[key] = value }),
    removeItem: vi.fn((key) => { delete store[key] }),
    clear: vi.fn(() => { Object.keys(store).forEach(key => delete store[key]) })
  }
}

/**
 * Mock router
 */
export function mockRouter() {
  return {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    currentRoute: {
      path: '/',
      params: {},
      query: {},
      name: null
    }
  }
}

/**
 * Mock route
 */
export function mockRoute() {
  return {
    path: '/',
    params: {},
    query: {},
    hash: '',
    fullPath: '/',
    matched: [],
    meta: {},
    name: null
  }
}

