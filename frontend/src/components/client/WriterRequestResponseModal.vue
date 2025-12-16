<template>
  <Modal
    :is-open="isOpen"
    :title="'Respond to Writer Request'"
    @close="$emit('close')"
    size="lg"
  >
    <div v-if="writerRequest" class="space-y-6">
      <!-- Request Details -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 class="font-semibold text-blue-900 mb-3">Request Details</h3>
        <div class="space-y-2 text-sm">
          <div>
            <span class="font-medium">Request Type:</span>
            <span class="ml-2 capitalize">{{ formatRequestType(writerRequest.request_type) }}</span>
          </div>
          <div v-if="writerRequest.additional_pages">
            <span class="font-medium">Additional Pages:</span>
            <span class="ml-2">{{ writerRequest.additional_pages }}</span>
          </div>
          <div v-if="writerRequest.additional_slides">
            <span class="font-medium">Additional Slides:</span>
            <span class="ml-2">{{ writerRequest.additional_slides }}</span>
          </div>
          <div>
            <span class="font-medium">Estimated Cost:</span>
            <span class="ml-2 font-semibold text-blue-700">${{ formatCurrency(writerRequest.estimated_cost || writerRequest.final_cost || 0) }}</span>
          </div>
          <div>
            <span class="font-medium">Writer's Reason:</span>
            <p class="mt-1 text-gray-700 bg-white p-2 rounded">{{ writerRequest.request_reason }}</p>
          </div>
        </div>
      </div>

      <!-- Response Options -->
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Your Response <span class="text-red-500">*</span>
          </label>
          <div class="space-y-2">
            <label class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
                   :class="responseType === 'accept' ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'">
              <input
                v-model="responseType"
                type="radio"
                value="accept"
                class="mr-3"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-900">Accept & Pay</div>
                <div class="text-xs text-gray-600 mt-1">Accept the request and proceed with payment</div>
              </div>
            </label>

            <label class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
                   :class="responseType === 'counter' ? 'border-yellow-500 bg-yellow-50' : 'border-gray-200 hover:border-gray-300'">
              <input
                v-model="responseType"
                type="radio"
                value="counter"
                class="mr-3"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-900">Counter Offer</div>
                <div class="text-xs text-gray-600 mt-1">Propose a different amount or quantity</div>
              </div>
            </label>

            <label class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
                   :class="responseType === 'reject' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
              <input
                v-model="responseType"
                type="radio"
                value="reject"
                class="mr-3"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-900">Reject</div>
                <div class="text-xs text-gray-600 mt-1">Decline the request</div>
              </div>
            </label>
          </div>
        </div>

        <!-- Counter Offer Fields -->
        <div v-if="responseType === 'counter'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 space-y-4">
          <h4 class="font-semibold text-yellow-900">Counter Offer Details</h4>
          
          <div v-if="writerRequest.request_type === 'page_increase'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Counter Offer Pages
            </label>
            <input
              v-model.number="counterOffer.counter_pages"
              type="number"
              min="1"
              :max="writerRequest.additional_pages"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
              placeholder="Enter number of pages"
            />
            <p class="mt-1 text-xs text-gray-600">
              Original request: {{ writerRequest.additional_pages }} pages
            </p>
          </div>

          <div v-if="writerRequest.request_type === 'slide_increase'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Counter Offer Slides
            </label>
            <input
              v-model.number="counterOffer.counter_slides"
              type="number"
              min="1"
              :max="writerRequest.additional_slides"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
              placeholder="Enter number of slides"
            />
            <p class="mt-1 text-xs text-gray-600">
              Original request: {{ writerRequest.additional_slides }} slides
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Counter Offer Amount (Optional)
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
              <input
                v-model.number="counterOffer.counter_cost"
                type="number"
                step="0.01"
                min="0"
                class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                placeholder="Enter counter offer amount"
              />
            </div>
            <p class="mt-1 text-xs text-gray-600">
              Original estimated cost: ${{ formatCurrency(writerRequest.estimated_cost || writerRequest.final_cost || 0) }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Reason for Counter Offer <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="counterOffer.counter_reason"
              rows="3"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
              placeholder="Explain your counter offer..."
            ></textarea>
          </div>
        </div>

        <!-- Rejection Reason -->
        <div v-if="responseType === 'reject'">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Reason for Rejection <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="rejectionReason"
            rows="3"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            placeholder="Please provide a reason for rejecting this request..."
          ></textarea>
        </div>
      </div>

      <!-- Payment Info for Accept -->
      <div v-if="responseType === 'accept' && writerRequest.requires_payment" class="bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="flex items-start gap-3">
          <span class="text-2xl">💳</span>
          <div class="flex-1">
            <h4 class="font-semibold text-green-900 mb-1">Payment Required</h4>
            <p class="text-sm text-green-800">
              You will need to pay ${{ formatCurrency(writerRequest.final_cost || writerRequest.estimated_cost || 0) }} 
              to proceed with this request.
            </p>
            <p class="text-xs text-green-700 mt-2">
              Payment will be processed after you accept this request.
            </p>
          </div>
        </div>
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
          type="button"
          @click="handleSubmit"
          :disabled="loading || !isFormValid"
          :class="[
            'px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors',
            getSubmitButtonClass(),
            { 'opacity-50 cursor-not-allowed': loading || !isFormValid }
          ]"
        >
          <span v-if="loading">Processing...</span>
          <span v-else>{{ getSubmitButtonText() }}</span>
        </button>
      </div>
    </div>
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
  writerRequest: {
    type: Object,
    default: null
  },
  orderId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const responseType = ref('accept')
const rejectionReason = ref('')
const counterOffer = ref({
  counter_pages: null,
  counter_slides: null,
  counter_cost: null,
  counter_reason: ''
})

const loading = ref(false)
const error = ref(null)

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const formatRequestType = (type) => {
  const types = {
    'page_increase': 'Page Increase',
    'slide_increase': 'Slide Increase',
    'deadline_extension': 'Deadline Extension'
  }
  return types[type] || type
}

const isFormValid = computed(() => {
  if (!responseType.value) return false
  
  if (responseType.value === 'reject') {
    return !!rejectionReason.value.trim()
  }
  
  if (responseType.value === 'counter') {
    const hasCounterValue = 
      (props.writerRequest?.request_type === 'page_increase' && counterOffer.value.counter_pages) ||
      (props.writerRequest?.request_type === 'slide_increase' && counterOffer.value.counter_slides)
    return hasCounterValue && !!counterOffer.value.counter_reason.trim()
  }
  
  return true // Accept
})

const getSubmitButtonText = () => {
  if (responseType.value === 'accept') return 'Accept & Pay'
  if (responseType.value === 'counter') return 'Send Counter Offer'
  return 'Reject Request'
}

const getSubmitButtonClass = () => {
  if (responseType.value === 'accept') return 'bg-green-600 hover:bg-green-700'
  if (responseType.value === 'counter') return 'bg-yellow-600 hover:bg-yellow-700'
  return 'bg-red-600 hover:bg-red-700'
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields'
    return
  }

  loading.value = true
  error.value = null

  try {
    let response
    
    if (responseType.value === 'accept') {
      // Accept and pay
      response = await ordersApi.clientRespondToWriterRequest(props.orderId, props.writerRequest.id, {
        response: 'approve'
      })
    } else if (responseType.value === 'counter') {
      // Counter offer
      response = await ordersApi.clientRespondToWriterRequest(props.orderId, props.writerRequest.id, {
        response: 'counter',
        counter_offer: {
          counter_pages: counterOffer.value.counter_pages,
          counter_slides: counterOffer.value.counter_slides,
          counter_cost: counterOffer.value.counter_cost,
          counter_reason: counterOffer.value.counter_reason
        }
      })
    } else {
      // Reject
      response = await ordersApi.clientRespondToWriterRequest(props.orderId, props.writerRequest.id, {
        response: 'reject',
        reason: rejectionReason.value
      })
    }

    emit('success', response.data)
    resetForm()
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to submit response'
    console.error('Response submission error:', err)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  responseType.value = 'accept'
  rejectionReason.value = ''
  counterOffer.value = {
    counter_pages: null,
    counter_slides: null,
    counter_cost: null,
    counter_reason: ''
  }
  error.value = null
}

watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    resetForm()
  } else if (props.writerRequest) {
    // Pre-fill counter offer with original values
    if (props.writerRequest.additional_pages) {
      counterOffer.value.counter_pages = props.writerRequest.additional_pages
    }
    if (props.writerRequest.additional_slides) {
      counterOffer.value.counter_slides = props.writerRequest.additional_slides
    }
  }
})
</script>
