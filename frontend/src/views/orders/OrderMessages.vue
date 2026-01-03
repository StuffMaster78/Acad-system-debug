<template>
  <div class="space-y-6 p-6">
    <div v-if="loading" class="flex items-center justify-center min-h-[400px]">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400">Loading order messages...</p>
      </div>
    </div>

    <div v-else-if="error" class="flex items-center justify-center min-h-[400px]">
      <div class="text-center">
        <div class="text-red-500 text-6xl mb-4">⚠️</div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Failed to Load Order</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
        <router-link
          :to="`/orders/${orderId}`"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-block"
        >
          ← Back to Order
        </router-link>
      </div>
    </div>

    <div v-else class="space-y-6">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Order Messages</h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">Order #{{ orderId }} • {{ orderTopic || 'N/A' }}</p>
        </div>
        <router-link
          :to="`/orders/${orderId}`"
          class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          ← Back to Order
        </router-link>
      </div>

      <!-- Use the new tabbed messaging component -->
      <OrderMessagesTabbed
        v-if="orderId"
        :order-id="orderId"
        :order-topic="orderTopic"
      />
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
