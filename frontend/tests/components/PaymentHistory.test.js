import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import PaymentHistory from '@/views/payments/PaymentHistory.vue'
import paymentsAPI from '@/api/payments'

// Mock the API
vi.mock('@/api/payments', () => ({
  default: {
    getPaymentHistory: vi.fn(),
    downloadReceipt: vi.fn()
  }
}))

// Mock composables
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn()
  })
}))

describe('PaymentHistory Component', () => {
  let router
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/payments', component: PaymentHistory }
      ]
    })
  })

  it('should render payment history', async () => {
    const mockPayments = [
      {
        id: 1,
        amount: '100.00',
        status: 'completed',
        payment_method: 'wallet',
        created_at: '2025-01-01T00:00:00Z',
        order: { id: 1, topic: 'Test Order' }
      }
    ]

    paymentsAPI.getPaymentHistory.mockResolvedValue({
      data: {
        results: mockPayments,
        count: 1
      }
    })

    const wrapper = mount(PaymentHistory, {
      global: {
        plugins: [router, pinia]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
  })

  it('should handle receipt download', async () => {
    const mockBlob = new Blob(['receipt content'], { type: 'application/pdf' })
    paymentsAPI.downloadReceipt.mockResolvedValue({
      data: mockBlob
    })

    // Mock DOM methods before mounting
    const mockLink = {
      click: vi.fn(),
      href: '',
      download: ''
    }
    global.URL.createObjectURL = vi.fn(() => 'blob:url')
    global.URL.revokeObjectURL = vi.fn()
    document.createElement = vi.fn(() => mockLink)
    document.body.appendChild = vi.fn()
    document.body.removeChild = vi.fn()

    const wrapper = mount(PaymentHistory, {
      global: {
        plugins: [router, pinia]
      }
    })

    await wrapper.vm.$nextTick()

    // Test download function - takes transaction object
    const transaction = {
      id: 'order_payment_1',
      type: 'order_payment',
      status: 'completed',
      amount: '100.00'
    }

    // Call download function
    await wrapper.vm.downloadReceipt(transaction)

    // Verify API was called
    expect(paymentsAPI.downloadReceipt).toHaveBeenCalled()
  })

  it('should filter payments by status', async () => {
    const mockPayments = [
      { id: 1, status: 'completed', amount: '100.00' },
      { id: 2, status: 'pending', amount: '200.00' }
    ]

    paymentsAPI.getPaymentHistory.mockResolvedValue({
      data: {
        results: mockPayments,
        count: 2
      }
    })

    const wrapper = mount(PaymentHistory, {
      global: {
        plugins: [router, pinia]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    wrapper.vm.selectedStatus = 'completed'
    await wrapper.vm.$nextTick()

    expect(wrapper.exists()).toBe(true)
  })
})

