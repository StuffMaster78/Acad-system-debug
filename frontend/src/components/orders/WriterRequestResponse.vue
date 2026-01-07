<template>
  <div class="space-y-4">
    <div
      v-for="request in requests"
      :key="request.id"
      class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6"
    >
      <!-- Request Header -->
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-2">
            <span
              class="px-3 py-1 rounded-lg text-sm font-semibold"
              :class="getStatusClass(request.status)"
            >
              {{ formatStatus(request.status) }}
            </span>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              {{ formatRequestType(request.request_type) }}
            </span>
          </div>
          <p class="text-sm text-gray-700 dark:text-gray-300 mt-2">
            {{ request.request_reason }}
          </p>
        </div>
        <div class="text-right">
          <div class="text-sm font-bold text-gray-900 dark:text-gray-100">
            ${{ formatCurrency(request.final_cost || request.estimated_cost) }}
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400">
            {{ formatDate(request.created_at) }}
          </div>
        </div>
      </div>

      <!-- Request Details -->
      <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 mb-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div v-if="request.additional_pages">
            <span class="text-gray-600 dark:text-gray-400">Additional Pages:</span>
            <span class="font-semibold text-gray-900 dark:text-gray-100 ml-2">
              {{ request.additional_pages }}
            </span>
          </div>
          <div v-if="request.additional_slides">
            <span class="text-gray-600 dark:text-gray-400">Additional Slides:</span>
            <span class="font-semibold text-gray-900 dark:text-gray-100 ml-2">
              {{ request.additional_slides }}
            </span>
          </div>
          <div v-if="request.new_deadline">
            <span class="text-gray-600 dark:text-gray-400">New Deadline:</span>
            <span class="font-semibold text-gray-900 dark:text-gray-100 ml-2">
              {{ formatDate(request.new_deadline) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Counter Offer Display -->
      <div v-if="request.has_counter_offer" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-4">
        <div class="flex items-start gap-2">
          <ExclamationTriangleIcon class="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5" />
          <div class="flex-1">
            <p class="text-sm font-semibold text-amber-900 dark:text-amber-300 mb-1">
              Counter Offer Received
            </p>
            <p class="text-sm text-amber-700 dark:text-amber-400">
              {{ request.client_counter_reason }}
            </p>
            <div v-if="request.client_counter_pages || request.client_counter_slides" class="mt-2 text-sm">
              <span v-if="request.client_counter_pages" class="text-amber-700 dark:text-amber-400">
                Pages: {{ request.client_counter_pages }}
              </span>
              <span v-if="request.client_counter_slides" class="text-amber-700 dark:text-amber-400 ml-3">
                Slides: {{ request.client_counter_slides }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions (only for pending requests) -->
      <div v-if="request.status === 'pending'" class="flex items-center gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="handleAccept(request)"
          :disabled="responding"
          class="flex-1 px-4 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <CheckIcon class="w-5 h-5" />
          Accept
        </button>
        <button
          @click="showCounterOfferModal = true; selectedRequest = request"
          :disabled="responding"
          class="px-4 py-2.5 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <HandRaisedIcon class="w-5 h-5" />
          Counter Offer
        </button>
        <button
          @click="handleDecline(request)"
          :disabled="responding"
          class="px-4 py-2.5 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <XMarkIcon class="w-5 h-5" />
          Decline
        </button>
      </div>
    </div>

    <!-- Counter Offer Modal -->
    <div
      v-if="showCounterOfferModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showCounterOfferModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
          Make Counter Offer
        </h3>
        <form @submit.prevent="handleCounterOffer" class="space-y-4">
          <div v-if="selectedRequest?.request_type === 'page_increase'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Counter Pages
            </label>
            <input
              v-model.number="counterOffer.counter_pages"
              type="number"
              min="1"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
            />
          </div>
          <div v-if="selectedRequest?.request_type === 'slide_increase'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Counter Slides
            </label>
            <input
              v-model.number="counterOffer.counter_slides"
              type="number"
              min="1"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Reason *
            </label>
            <textarea
              v-model="counterOffer.counter_reason"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
              required
            ></textarea>
          </div>
          <div class="flex items-center gap-3 pt-4">
            <button
              type="submit"
              :disabled="responding || !counterOffer.counter_reason"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-semibold disabled:opacity-50"
            >
              Submit Counter Offer
            </button>
            <button
              type="button"
              @click="showCounterOfferModal = false"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { CheckIcon, XMarkIcon, HandRaisedIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import writerRequestsAPI from '@/api/writer-requests'
import { useRouter } from 'vue-router'

const props = defineProps({
  requests: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['updated'])

const router = useRouter()
const responding = ref(false)
const showCounterOfferModal = ref(false)
const selectedRequest = ref(null)
const counterOffer = ref({
  counter_pages: null,
  counter_slides: null,
  counter_reason: ''
})

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatStatus = (status) => {
  const statusMap = {
    pending: 'Pending',
    accepted: 'Accepted',
    declined: 'Declined'
  }
  return statusMap[status] || status
}

const formatRequestType = (type) => {
  const typeMap = {
    page_increase: 'Page Increase',
    slide_increase: 'Slide Increase',
    deadline_extension: 'Deadline Extension'
  }
  return typeMap[type] || type
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    accepted: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    declined: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const handleAccept = async (request) => {
  responding.value = true
  try {
    const response = await writerRequestsAPI.clientRespond(request.id, {
      action: 'accept'
    })

    if (response.data.requires_payment) {
      // Redirect to payment
      router.push(response.data.payment_url)
    } else {
      emit('updated')
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to accept request')
  } finally {
    responding.value = false
  }
}

const handleDecline = async (request) => {
  if (!confirm('Are you sure you want to decline this request?')) {
    return
  }

  responding.value = true
  try {
    await writerRequestsAPI.clientRespond(request.id, {
      action: 'decline',
      reason: 'Declined by client'
    })
    emit('updated')
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to decline request')
  } finally {
    responding.value = false
  }
}

const handleCounterOffer = async () => {
  if (!selectedRequest.value || !counterOffer.value.counter_reason) {
    return
  }

  responding.value = true
  try {
    await writerRequestsAPI.clientRespond(selectedRequest.value.id, {
      action: 'counteroffer',
      ...counterOffer.value
    })
    showCounterOfferModal.value = false
    selectedRequest.value = null
    counterOffer.value = {
      counter_pages: null,
      counter_slides: null,
      counter_reason: ''
    }
    emit('updated')
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to submit counter offer')
  } finally {
    responding.value = false
  }
}
</script>

