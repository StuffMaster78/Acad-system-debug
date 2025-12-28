<template>
  <div class="space-y-4">
    <!-- Payment Status -->
    <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Payment Status</p>
          <p class="text-lg font-semibold" :class="order.is_paid ? 'text-green-600' : 'text-yellow-600'">
            {{ order.is_paid ? 'Paid' : 'Unpaid' }}
          </p>
        </div>
        <button
          v-if="!order.is_paid"
          @click="markAsPaid"
          :disabled="processing"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          {{ processing ? 'Processing...' : 'Mark as Paid' }}
        </button>
        <button
          v-else
          @click="markAsUnpaid"
          :disabled="processing"
          class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 transition-colors"
        >
          Mark as Unpaid
        </button>
      </div>
    </div>

    <!-- Financial Summary -->
    <div class="grid grid-cols-2 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-600 dark:text-gray-400">Total Price</p>
        <p class="text-xl font-bold text-gray-900 dark:text-white">
          ${{ parseFloat(order.total_price || 0).toFixed(2) }}
        </p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-600 dark:text-gray-400">Writer Compensation</p>
        <p class="text-xl font-bold text-gray-900 dark:text-white">
          ${{ parseFloat(order.writer_compensation || 0).toFixed(2) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ordersAPI } from '@/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  order: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['success', 'error'])

const { success: showSuccessToast, error: showErrorToast } = useToast()

const processing = ref(false)

const markAsPaid = async () => {
  processing.value = true
  try {
    await ordersAPI.executeAction(props.order.id, { action: 'mark_paid' })
    showSuccessToast('Order marked as paid!')
    emit('success', { action: 'mark_paid' })
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to mark as paid'
    showErrorToast(errorMsg)
    emit('error', error)
  } finally {
    processing.value = false
  }
}

const markAsUnpaid = async () => {
  processing.value = true
  try {
    await ordersAPI.executeAction(props.order.id, { action: 'mark_unpaid' })
    showSuccessToast('Order marked as unpaid!')
    emit('success', { action: 'mark_unpaid' })
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to mark as unpaid'
    showErrorToast(errorMsg)
    emit('error', error)
  } finally {
    processing.value = false
  }
}
</script>

