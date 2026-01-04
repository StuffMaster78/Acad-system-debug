<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Breadcrumbs -->
      <nav class="mb-6" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-2 text-sm">
          <li>
            <router-link to="/orders" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Orders
            </router-link>
          </li>
          <li class="text-gray-400 dark:text-gray-600">/</li>
          <li>
            <router-link :to="`/orders/${orderId}`" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Order #{{ orderId }}
            </router-link>
          </li>
          <li class="text-gray-400 dark:text-gray-600">/</li>
          <li class="text-gray-900 dark:text-gray-100 font-medium">Messages</li>
        </ol>
      </nav>

      <div v-if="loading" class="flex items-center justify-center min-h-[500px]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600 dark:text-gray-400 text-lg">Loading order messages...</p>
        </div>
      </div>

      <div v-else-if="error" class="flex items-center justify-center min-h-[500px]">
        <div class="text-center max-w-md">
          <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
            <svg class="w-10 h-10 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Failed to Load Order</h2>
          <p class="text-gray-600 dark:text-gray-400 mb-6">{{ error }}</p>
          <router-link
            :to="`/orders/${orderId}`"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm hover:shadow-md"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Order
          </router-link>
        </div>
      </div>

      <div v-else class="space-y-6">
        <!-- Header Section -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <div>
                  <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Order Messages</h1>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Order #{{ orderId }} • {{ orderTopic || 'N/A' }}
                  </p>
                </div>
              </div>
            </div>
            <router-link
              :to="`/orders/${orderId}`"
              class="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Order
            </router-link>
          </div>
        </div>

        <!-- Messages Component -->
        <OrderMessagesTabbed
          v-if="orderId"
          :order-id="orderId"
          :order-topic="orderTopic"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OrderMessagesTabbed from '@/components/order/OrderMessagesTabbed.vue'
import ordersAPI from '@/api/orders'

const route = useRoute()
const router = useRouter()
const orderId = computed(() => {
  const id = route.params.id
  if (!id) return null
  const parsed = parseInt(id)
  return isNaN(parsed) ? null : parsed
})
const orderTopic = ref('')
const loading = ref(true)
const error = ref(null)

// Load order to get topic
onMounted(async () => {
  if (!orderId.value) {
    error.value = 'Invalid order ID'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null
    const res = await ordersAPI.get(orderId.value)
    if (res?.data) {
      orderTopic.value = res.data.topic || ''
    } else {
      error.value = 'Order not found'
    }
  } catch (err) {
    console.error('Failed to load order:', err)
    if (err.response?.status === 404) {
      error.value = 'Order not found'
    } else if (err.response?.status === 403) {
      error.value = 'You do not have permission to view this order'
    } else {
      error.value = err.response?.data?.detail || err.message || 'Failed to load order'
    }
  } finally {
    loading.value = false
  }
})
</script>
