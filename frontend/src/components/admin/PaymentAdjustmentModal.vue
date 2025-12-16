<template>
  <Modal
    :is-open="isOpen"
    :title="'Adjust Payment Amount'"
    @close="$emit('close')"
    size="md"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <div class="text-sm text-blue-800">
          <p class="font-semibold mb-2">Payment Information:</p>
          <div class="space-y-1 text-sm">
            <div><span class="font-medium">Writer:</span> {{ payment?.writer_name || 'N/A' }}</div>
            <div><span class="font-medium">Current Amount:</span> ${{ formatCurrency(payment?.amount || 0) }}</div>
            <div v-if="payment?.order_id">
              <span class="font-medium">Order:</span> #{{ payment.order_id }}
            </div>
            <div v-if="payment?.payment_set_by">
              <span class="font-medium">Payment Type:</span> 
              <span class="capitalize">{{ payment.payment_set_by.replace('_', ' ') }}</span>
            </div>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Adjustment Amount <span class="text-red-500">*</span>
        </label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
          <input
            v-model.number="form.adjustment_amount"
            type="number"
            step="0.01"
            min="-999999.99"
            max="999999.99"
            required
            class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Enter amount (positive to increase, negative to decrease)"
          />
        </div>
        <p class="mt-1 text-xs text-gray-500">
          Positive values increase payment, negative values decrease payment
        </p>
        <div v-if="form.adjustment_amount" class="mt-2 p-2 bg-gray-50 rounded text-sm">
          <span class="text-gray-600">New Amount:</span>
          <span class="font-semibold ml-2" :class="getNewAmountClass()">
            ${{ formatCurrency((payment?.amount || 0) + parseFloat(form.adjustment_amount || 0)) }}
          </span>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Reason <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="form.reason"
          rows="4"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder="Enter reason for adjustment (e.g., Additional pages added, Correction, etc.)"
        ></textarea>
        <p class="mt-1 text-xs text-gray-500">
          This reason will be logged for audit purposes
        </p>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>

      <div class="flex justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          @click="$emit('close')"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="loading || !form.adjustment_amount || !form.reason"
          class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">Adjusting...</span>
          <span v-else>Adjust Payment</span>
        </button>
      </div>
    </form>
  </Modal>
</template>

<script setup>
import { ref, watch } from 'vue'
import Modal from '@/components/common/Modal.vue'
import writerPaymentsApi from '@/api/writer-payments'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  payment: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const form = ref({
  adjustment_amount: null,
  reason: ''
})

const loading = ref(false)
const error = ref(null)

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const getNewAmountClass = () => {
  const newAmount = (props.payment?.amount || 0) + parseFloat(form.value.adjustment_amount || 0)
  if (newAmount < 0) return 'text-red-600'
  if (newAmount > (props.payment?.amount || 0)) return 'text-green-600'
  return 'text-gray-900'
}

const handleSubmit = async () => {
  if (!form.value.adjustment_amount || !form.value.reason) {
    error.value = 'Please fill in all required fields'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await writerPaymentsApi.adjustPaymentAmount(
      props.payment.id,
      {
        adjustment_amount: parseFloat(form.value.adjustment_amount),
        reason: form.value.reason
      }
    )

    emit('success', response.data)
    resetForm()
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to adjust payment'
    console.error('Payment adjustment error:', err)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    adjustment_amount: null,
    reason: ''
  }
  error.value = null
}

watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})
</script>
