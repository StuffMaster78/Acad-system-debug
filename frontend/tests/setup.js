/**
 * Vitest setup file
 * 
 * This file runs before all tests and sets up the testing environment.
 */
import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
}

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock Element.setAttribute for Vue scoped CSS in test environment
// Vue tries to set scoped IDs on elements, but test elements might not have setAttribute
const originalCreateElement = document.createElement
document.createElement = function(tagName, options) {
  const element = originalCreateElement.call(document, tagName, options)
  if (!element.setAttribute) {
    element.setAttribute = vi.fn()
  }
  return element
}

// Mock fetch if needed
global.fetch = vi.fn()

// Configure Vue Test Utils
config.global.mocks = {
  $t: (key) => key, // Mock i18n
  $router: {
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
  },
  $route: {
    path: '/',
    params: {},
    query: {},
    hash: '',
    fullPath: '/',
    matched: [],
    meta: {},
    name: null,
  },
}

// Suppress console errors in tests (optional - remove if you want to see them)
const originalError = console.error
console.error = (...args) => {
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('[Vue warn]') || args[0].includes('Warning:'))
  ) {
    return
  }
  originalError.call(console, ...args)
}

