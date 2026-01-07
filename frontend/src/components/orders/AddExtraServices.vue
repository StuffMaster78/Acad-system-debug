<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <SparklesIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Additional Services
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Enhance your order with premium services
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loadingServices" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      <span class="ml-3 text-sm text-gray-600 dark:text-gray-400">Loading services...</span>
    </div>

    <!-- Services Grid -->
    <div v-else-if="availableServices.length > 0" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="service in availableServices"
          :key="service.id"
          @click="toggleService(service.id)"
          :class="[
            'border-2 rounded-xl p-5 cursor-pointer transition-all hover:shadow-md',
            selectedServices.includes(service.id)
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 shadow-md'
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          ]"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <input
                  type="checkbox"
                  :checked="selectedServices.includes(service.id)"
                  @change="toggleService(service.id)"
                  class="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                />
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">
                  {{ service.service_name }}
                </h4>
              </div>
              <p v-if="service.description" class="text-sm text-gray-600 dark:text-gray-400 mt-2">
                {{ service.description }}
              </p>
            </div>
            <div class="text-right">
              <div class="text-lg font-bold text-primary-600 dark:text-primary-400">
                ${{ formatCurrency(service.cost) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Services Summary -->
      <div v-if="selectedServices.length > 0" class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            Selected Services ({{ selectedServices.length }})
          </span>
          <span class="text-lg font-bold text-primary-600 dark:text-primary-400">
            ${{ formatCurrency(selectedTotal) }}
          </span>
        </div>
        <div class="flex flex-wrap gap-2 mt-2">
          <span
            v-for="serviceId in selectedServices"
            :key="serviceId"
            class="px-2 py-1 bg-white dark:bg-gray-700 text-sm text-gray-700 dark:text-gray-300 rounded border border-primary-200 dark:border-primary-700"
          >
            {{ getServiceName(serviceId) }}
          </span>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p class="text-sm text-red-700 dark:text-red-400">{{ error }}</p>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="handleSubmit"
          :disabled="loading || selectedServices.length === 0"
          class="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <ArrowPathIcon v-if="loading" class="w-5 h-5 animate-spin" />
          <span v-else>Add Services & Proceed to Payment</span>
        </button>
        <button
          @click="$emit('cancel')"
          class="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <SparklesIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <p class="text-sm text-gray-600 dark:text-gray-400">
        No additional services available at this time.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { SparklesIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import ordersAPI from '@/api/orders'
import pricingAPI from '@/api/pricing'

const props = defineProps({
  orderId: {
    type: [String, Number],
    required: true
  },
  existingServiceIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['success', 'cancel'])

const availableServices = ref([])
const selectedServices = ref([])
const loadingServices = ref(false)
const loading = ref(false)
const error = ref(null)

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const selectedTotal = computed(() => {
  return selectedServices.value.reduce((sum, serviceId) => {
    const service = availableServices.value.find(s => s.id === serviceId)
    return sum + (parseFloat(service?.cost || 0))
  }, 0)
})

const getServiceName = (serviceId) => {
  const service = availableServices.value.find(s => s.id === serviceId)
  return service?.service_name || 'Unknown Service'
}

const toggleService = (serviceId) => {
  const index = selectedServices.value.indexOf(serviceId)
  if (index > -1) {
    selectedServices.value.splice(index, 1)
  } else {
    selectedServices.value.push(serviceId)
  }
}

const loadAvailableServices = async () => {
  loadingServices.value = true
  error.value = null
  
  try {
    // Get order to determine website
    const orderResponse = await ordersAPI.get(props.orderId)
    const order = orderResponse.data
    
    // Load available services for the order's website
    // Note: The API should filter by website automatically via WebsiteScopedViewSetMixin
    const response = await pricingAPI.listAdditionalServices({
      is_active: true
    })
    
    // Filter out services already added to the order
    const existingIds = props.existingServiceIds || []
    const allServices = response.data.results || response.data || []
    
    // Also filter by website if available
    availableServices.value = allServices.filter(
      service => {
        // Check if service belongs to order's website
        const serviceWebsite = service.website || service.website_id
        const orderWebsite = order.website || order.website_id
        const matchesWebsite = !serviceWebsite || !orderWebsite || serviceWebsite === orderWebsite
        
        // Check if not already added
        const notAdded = !existingIds.includes(service.id)
        
        return matchesWebsite && notAdded
      }
    )
  } catch (err) {
    console.error('Failed to load services:', err)
    error.value = 'Failed to load available services. Please try again.'
    availableServices.value = []
  } finally {
    loadingServices.value = false
  }
}

const handleSubmit = async () => {
  if (selectedServices.value.length === 0) {
    error.value = 'Please select at least one service.'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await ordersAPI.addExtraServices(props.orderId, {
      service_ids: selectedServices.value
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
    error.value = err.response?.data?.detail || 'Failed to add services. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAvailableServices()
})
</script>

