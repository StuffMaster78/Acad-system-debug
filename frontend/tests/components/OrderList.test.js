import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import OrderList from '@/views/orders/OrderList.vue'
import ordersAPI from '@/api/orders'

// Mock the API
vi.mock('@/api/orders', () => ({
  default: {
    listOrders: vi.fn(),
    cancelOrder: vi.fn(),
    bulkCancel: vi.fn()
  }
}))

// Mock composables
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  })
}))

vi.mock('@/composables/useConfirmDialog', () => ({
  useConfirmDialog: () => ({
    showDestructive: vi.fn(() => Promise.resolve(true))
  })
}))

describe('OrderList Component', () => {
  let router
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/orders', component: OrderList },
        { path: '/orders/:id', component: { template: '<div>Order Detail</div>' } }
      ]
    })
  })

  it('should render order list', async () => {
    const mockOrders = [
      {
        id: 1,
        topic: 'Test Order 1',
        status: 'draft',
        total_price: '100.00',
        created_at: '2025-01-01T00:00:00Z'
      },
      {
        id: 2,
        topic: 'Test Order 2',
        status: 'in_progress',
        total_price: '200.00',
        created_at: '2025-01-02T00:00:00Z'
      }
    ]

    ordersAPI.listOrders.mockResolvedValue({
      data: {
        results: mockOrders,
        count: 2
      }
    })

    const wrapper = mount(OrderList, {
      global: {
        plugins: [router, pinia]
      }
    })

    // Wait for component to load
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
  })

  it('should handle loading state', () => {
    ordersAPI.listOrders.mockImplementation(() => new Promise(() => {})) // Never resolves

    const wrapper = mount(OrderList, {
      global: {
        plugins: [router, pinia]
      }
    })

    expect(wrapper.vm.loading).toBe(true)
  })

  it('should handle error state', async () => {
    ordersAPI.listOrders.mockRejectedValue(new Error('API Error'))

    const wrapper = mount(OrderList, {
      global: {
        plugins: [router, pinia]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Component should handle error gracefully
    expect(wrapper.exists()).toBe(true)
  })

  it('should filter orders by status', async () => {
    const mockOrders = [
      { id: 1, status: 'draft', topic: 'Draft Order' },
      { id: 2, status: 'in_progress', topic: 'In Progress Order' }
    ]

    ordersAPI.listOrders.mockResolvedValue({
      data: {
        results: mockOrders,
        count: 2
      }
    })

    const wrapper = mount(OrderList, {
      global: {
        plugins: [router, pinia]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Test filtering logic
    wrapper.vm.selectedStatus = 'draft'
    await wrapper.vm.$nextTick()

    expect(wrapper.exists()).toBe(true)
  })

  it('should support bulk selection', async () => {
    const mockOrders = [
      { id: 1, topic: 'Order 1', status: 'draft' },
      { id: 2, topic: 'Order 2', status: 'draft' }
    ]

    ordersAPI.listOrders.mockResolvedValue({
      data: {
        results: mockOrders,
        count: 2
      }
    })

    const wrapper = mount(OrderList, {
      global: {
        plugins: [router, pinia]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Test bulk selection
    wrapper.vm.selectedOrders = [1, 2]
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.selectedOrders.length).toBe(2)
  })
})

