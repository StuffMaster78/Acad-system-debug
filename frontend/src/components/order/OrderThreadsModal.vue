<template>
  <div class="fixed inset-0 bg-gray-100 z-50 flex items-center justify-center" @click.self="close">
    <div class="bg-white rounded-lg w-full max-w-4xl h-[90vh] max-h-[800px] overflow-hidden flex flex-col shadow-xl">
      <!-- Header -->
      <div class="bg-primary-600 text-white px-4 py-3 flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold">Order Messages</h3>
          <p class="text-xs text-primary-100">
            Order #{{ orderId }}
            <span v-if="orderTopic">• {{ orderTopic }}</span>
          </p>
        </div>
        <button @click="close" class="text-white hover:text-gray-200 text-xl">✕</button>
      </div>

      <!-- Tabbed messages UI reused from order details/messages page -->
      <div class="flex-1 overflow-y-auto p-4">
        <OrderMessagesTabbed
          :order-id="orderId"
          :order-topic="orderTopic"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import ordersAPI from '@/api/orders'
import OrderMessagesTabbed from '@/components/order/OrderMessagesTabbed.vue'

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  initialThreadId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close'])

const orderTopic = ref('')

const close = () => {
  emit('close')
}

onMounted(() => {
  // Load order topic for context in header and tabbed component
  ordersAPI.get(props.orderId)
    .then(res => {
      orderTopic.value = res.data.topic || ''
    })
    .catch(() => {
      orderTopic.value = ''
    })
})

watch(() => props.orderId, () => {
  ordersAPI.get(props.orderId)
    .then(res => {
      orderTopic.value = res.data.topic || ''
    })
    .catch(() => {
      orderTopic.value = ''
    })
})
</script>
