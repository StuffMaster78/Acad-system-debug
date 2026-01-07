<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <DocumentPlusIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Request Additional Pages or Slides
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Request the client to add more pages or slides to this order
        </p>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Request Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Request Type *
          </label>
          <select
            v-model="form.request_type"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
            required
          >
            <option value="">Select type...</option>
            <option value="page_increase">Page Increase</option>
            <option value="slide_increase">Slide Increase</option>
          </select>
        </div>

        <!-- Additional Pages (conditional) -->
        <div v-if="form.request_type === 'page_increase'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Additional Pages *
          </label>
          <input
            v-model.number="form.additional_pages"
            type="number"
            min="1"
            step="1"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="Enter number of pages"
            required
          />
        </div>

        <!-- Additional Slides (conditional) -->
        <div v-if="form.request_type === 'slide_increase'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Additional Slides *
          </label>
          <input
            v-model.number="form.additional_slides"
            type="number"
            min="1"
            step="1"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="Enter number of slides"
            required
          />
        </div>
      </div>

      <!-- Request Reason -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Reason for Request *
        </label>
        <textarea
          v-model="form.request_reason"
          rows="4"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
          placeholder="Explain why you need additional pages/slides..."
          required
        ></textarea>
      </div>

      <!-- Cost Preview -->
      <div v-if="costPreview" class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Estimated Cost:</span>
          <span class="text-lg font-bold text-primary-600 dark:text-primary-400">
            ${{ formatCurrency(costPreview.final_cost || costPreview.estimated_cost) }}
          </span>
        </div>
        <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
          This is an estimate. Final cost may vary based on client approval.
        </p>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p class="text-sm text-red-700 dark:text-red-400">{{ error }}</p>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3 pt-4">
        <button
          type="submit"
          :disabled="loading || !form.request_type || !form.request_reason"
          class="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <ArrowPathIcon v-if="loading" class="w-5 h-5 animate-spin" />
          <span v-else>Submit Request</span>
        </button>
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { DocumentPlusIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import writerRequestsAPI from '@/api/writer-requests'

const props = defineProps({
  orderId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['success', 'cancel'])

const form = ref({
  request_type: '',
  additional_pages: null,
  additional_slides: null,
  request_reason: ''
})

const loading = ref(false)
const error = ref(null)
const costPreview = ref(null)

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

// Watch for changes to fetch cost preview
watch([() => form.value.request_type, () => form.value.additional_pages, () => form.value.additional_slides], async ([type, pages, slides]) => {
  if (type && ((type === 'page_increase' && pages > 0) || (type === 'slide_increase' && slides > 0))) {
    try {
      const response = await writerRequestsAPI.getPricingPreview({
        order_id: props.orderId,
        request_type: type,
        additional_pages: type === 'page_increase' ? pages : 0,
        additional_slides: type === 'slide_increase' ? slides : 0
      })
      costPreview.value = response.data
    } catch (err) {
      // Silently fail preview
      costPreview.value = null
    }
  } else {
    costPreview.value = null
  }
})

const handleSubmit = async () => {
  if (!form.value.request_type) {
    error.value = 'Please select a request type.'
    return
  }

  if (form.value.request_type === 'page_increase' && !form.value.additional_pages) {
    error.value = 'Please specify the number of additional pages.'
    return
  }

  if (form.value.request_type === 'slide_increase' && !form.value.additional_slides) {
    error.value = 'Please specify the number of additional slides.'
    return
  }

  if (!form.value.request_reason) {
    error.value = 'Please provide a reason for your request.'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await writerRequestsAPI.createRequest({
      order_id: props.orderId,
      request_type: form.value.request_type,
      request_reason: form.value.request_reason,
      additional_pages: form.value.additional_pages || null,
      additional_slides: form.value.additional_slides || null
    })

    emit('success', response.data)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to submit request. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

