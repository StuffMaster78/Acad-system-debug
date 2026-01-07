<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <PlusIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Add Pages or Slides
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Add additional pages or slides to your order
        </p>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Additional Pages -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Additional Pages
          </label>
          <input
            v-model.number="form.additional_pages"
            type="number"
            min="0"
            step="1"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="0"
          />
        </div>

        <!-- Additional Slides -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Additional Slides
          </label>
          <input
            v-model.number="form.additional_slides"
            type="number"
            min="0"
            step="1"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="0"
          />
        </div>
      </div>

      <!-- Cost Preview -->
      <div v-if="costPreview" class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Estimated Cost:</span>
          <span class="text-lg font-bold text-primary-600 dark:text-primary-400">
            ${{ formatCurrency(costPreview) }}
          </span>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p class="text-sm text-red-700 dark:text-red-400">{{ error }}</p>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3 pt-4">
        <button
          type="submit"
          :disabled="loading || (!form.additional_pages && !form.additional_slides) || (form.additional_pages <= 0 && form.additional_slides <= 0)"
          class="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <ArrowPathIcon v-if="loading" class="w-5 h-5 animate-spin" />
          <span v-else>Add & Proceed to Payment</span>
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
import { PlusIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import ordersAPI from '@/api/orders'

const props = defineProps({
  orderId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['success', 'cancel'])

const form = ref({
  additional_pages: 0,
  additional_slides: 0
})

const loading = ref(false)
const error = ref(null)
const costPreview = ref(null)

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

// Watch for changes to calculate cost preview
watch([() => form.value.additional_pages, () => form.value.additional_slides], async ([pages, slides]) => {
  if ((pages > 0 || slides > 0) && !loading.value) {
    // Could fetch cost preview from API if available
    // For now, we'll calculate it after submission
  } else {
    costPreview.value = null
  }
})

const handleSubmit = async () => {
  if (form.value.additional_pages <= 0 && form.value.additional_slides <= 0) {
    error.value = 'Please specify at least one page or slide to add.'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await ordersAPI.addPagesSlides(props.orderId, {
      additional_pages: form.value.additional_pages || 0,
      additional_slides: form.value.additional_slides || 0
    })

    if (response.data.requires_payment) {
      // Redirect to payment page
      emit('success', {
        ...response.data,
        redirectToPayment: true,
        paymentUrl: response.data.payment_url
      })
    } else {
      // Success without payment
      emit('success', response.data)
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add pages/slides. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

