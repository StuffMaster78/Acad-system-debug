<template>
  <Modal
    :is-open="isOpen"
    :title="'Request Additional Pages/Slides'"
    @close="$emit('close')"
    size="md"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <div class="text-sm text-blue-800">
          <p class="font-semibold mb-2">Order Information:</p>
          <div class="space-y-1 text-sm">
            <div><span class="font-medium">Order ID:</span> #{{ order?.id }}</div>
            <div><span class="font-medium">Topic:</span> {{ order?.topic || 'N/A' }}</div>
            <div><span class="font-medium">Current Pages:</span> {{ order?.number_of_pages || 0 }}</div>
            <div><span class="font-medium">Current Slides:</span> {{ order?.number_of_slides || 0 }}</div>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Request Type <span class="text-red-500">*</span>
        </label>
        <div class="space-y-2">
          <label class="flex items-center">
            <input
              v-model="form.request_type"
              type="radio"
              value="page_increase"
              class="mr-2"
            />
            <span>Page Increase</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="form.request_type"
              type="radio"
              value="slide_increase"
              class="mr-2"
            />
            <span>Slide Increase</span>
          </label>
        </div>
      </div>

      <div v-if="form.request_type === 'page_increase'">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Additional Pages <span class="text-red-500">*</span>
        </label>
        <input
          v-model.number="form.additional_pages"
          type="number"
          min="1"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder="Enter number of additional pages"
        />
        <p class="mt-1 text-xs text-gray-500">
          New total: {{ (order?.number_of_pages || 0) + (form.additional_pages || 0) }} pages
        </p>
      </div>

      <div v-if="form.request_type === 'slide_increase'">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Additional Slides <span class="text-red-500">*</span>
        </label>
        <input
          v-model.number="form.additional_slides"
          type="number"
          min="1"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder="Enter number of additional slides"
        />
        <p class="mt-1 text-xs text-gray-500">
          New total: {{ (order?.number_of_slides || 0) + (form.additional_slides || 0) }} slides
        </p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Reason <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="form.request_reason"
          rows="4"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder="Explain why you need additional pages/slides..."
        ></textarea>
        <p class="mt-1 text-xs text-gray-500">
          This request will be sent to the client for approval
        </p>
      </div>

      <div v-if="estimatedCost" class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
        <p class="text-sm text-yellow-800">
          <span class="font-semibold">Estimated Additional Cost:</span> ${{ formatCurrency(estimatedCost) }}
        </p>
        <p class="text-xs text-yellow-700 mt-1">
          This is an estimate. Final cost may vary after client approval.
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
          :disabled="loading || !isFormValid"
          class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">Submitting...</span>
          <span v-else>Submit Request</span>
        </button>
      </div>
    </form>
  </Modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Modal from '@/components/common/Modal.vue'
import ordersApi from '@/api/orders'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const form = ref({
  request_type: 'page_increase',
  additional_pages: null,
  additional_slides: null,
  request_reason: ''
})

const loading = ref(false)
const error = ref(null)
const estimatedCost = ref(null)

const isFormValid = computed(() => {
  if (!form.value.request_reason) return false
  if (form.value.request_type === 'page_increase' && !form.value.additional_pages) return false
  if (form.value.request_type === 'slide_increase' && !form.value.additional_slides) return false
  return true
})

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const calculateEstimatedCost = async () => {
  if (!props.order || !isFormValid.value) {
    estimatedCost.value = null
    return
  }

  try {
    // You may need to create an endpoint to preview the cost
    // For now, we'll skip this or use a simple calculation
    estimatedCost.value = null
  } catch (err) {
    console.error('Failed to calculate estimated cost:', err)
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields'
    return
  }

  loading.value = true
  error.value = null

  try {
    const requestData = {
      request_type: form.value.request_type,
      request_reason: form.value.request_reason
    }

    if (form.value.request_type === 'page_increase') {
      requestData.additional_pages = form.value.additional_pages
    } else if (form.value.request_type === 'slide_increase') {
      requestData.additional_slides = form.value.additional_slides
    }

    // Create writer request using the orders API
    const response = await ordersApi.createWriterRequest(props.order.id, requestData)

    emit('success', response.data)
    resetForm()
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to submit request'
    console.error('Request submission error:', err)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    request_type: 'page_increase',
    additional_pages: null,
    additional_slides: null,
    request_reason: ''
  }
  error.value = null
  estimatedCost.value = null
}

watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

watch(() => [form.value.request_type, form.value.additional_pages, form.value.additional_slides], () => {
  calculateEstimatedCost()
})
</script>
