/**
 * Test utilities for Vue component testing
 */
import { mount, shallowMount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { vi } from 'vitest'

/**
 * Create a test router instance
 */
export function createTestRouter(routes = []) {
  return createRouter({
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        component: { template: '<div>Home</div>' }
      },
      ...routes
    ]
  })
}

/**
 * Create a test Pinia store instance
 */
export function createTestPinia() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

/**
 * Mount a component with default test setup
 */
export function mountComponent(component, options = {}) {
  const {
    router = createTestRouter(),
    pinia = createTestPinia(),
    props = {},
    slots = {},
    global = {},
    ...mountOptions
  } = options

  return mount(component, {
    global: {
      plugins: [router, pinia],
      stubs: {
        'router-link': true,
        'router-view': true,
      },
      mocks: {
        $t: (key) => key,
      },
      ...global,
    },
    props,
    slots,
    ...mountOptions,
  })
}

/**
 * Shallow mount a component with default test setup
 */
export function shallowMountComponent(component, options = {}) {
  const {
    router = createTestRouter(),
    pinia = createTestPinia(),
    props = {},
    slots = {},
    global = {},
    ...mountOptions
  } = options

  return shallowMount(component, {
    global: {
      plugins: [router, pinia],
      stubs: {
        'router-link': true,
        'router-view': true,
      },
      mocks: {
        $t: (key) => key,
      },
      ...global,
    },
    props,
    slots,
    ...mountOptions,
  })
}

/**
 * Wait for next tick
 */
export async function waitForNextTick() {
  await new Promise(resolve => setTimeout(resolve, 0))
}

/**
 * Wait for a specific amount of time
 */
export async function waitFor(ms = 100) {
  await new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Mock API response
 */
export function mockApiResponse(data, status = 200) {
  return {
    data,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: {},
    config: {},
  }
}

/**
 * Mock axios instance
 */
export function createMockAxios() {
  return {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    request: vi.fn(),
    interceptors: {
      request: { use: vi.fn(), eject: vi.fn() },
      response: { use: vi.fn(), eject: vi.fn() },
    },
  }
}

/**
 * Create a mock user object
 */
export function createMockUser(overrides = {}) {
  return {
    id: 1,
    email: 'test@example.com',
    username: 'testuser',
    role: 'client',
    first_name: 'Test',
    last_name: 'User',
    is_active: true,
    ...overrides,
  }
}

/**
 * Create a mock order object
 */
export function createMockOrder(overrides = {}) {
  return {
    id: 1,
    title: 'Test Order',
    description: 'Test Description',
    status: 'pending',
    price: '100.00',
    pages: 5,
    deadline: new Date().toISOString(),
    ...overrides,
  }
}

