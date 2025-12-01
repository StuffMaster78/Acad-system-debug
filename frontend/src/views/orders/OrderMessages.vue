<template>
  <div class="space-y-6 p-6">
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
      :order-id="orderId"
      :order-topic="orderTopic"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import OrderMessagesTabbed from '@/components/order/OrderMessagesTabbed.vue'
import ordersAPI from '@/api/orders'

const route = useRoute()
const orderId = computed(() => parseInt(route.params.id))
const orderTopic = ref('')

// Load order to get topic
onMounted(async () => {
  try {
    const res = await ordersAPI.get(orderId.value)
    orderTopic.value = res.data.topic || ''
  } catch (error) {
    console.error('Failed to load order:', error)
  }
})
</script>
