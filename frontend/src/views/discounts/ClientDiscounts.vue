<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Available Discounts</h1>
        <p class="mt-2 text-gray-600">Browse and use available discount codes</p>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by code or description..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Type</label>
          <select v-model="filters.discount_type" @change="loadDiscounts" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="fixed">Fixed Amount</option>
            <option value="percent">Percentage</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Discounts Grid -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="!discounts.length" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <p class="text-gray-500 text-lg">No discounts available at the moment.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="discount in discounts"
        :key="discount.id"
        class="bg-white rounded-lg shadow-sm p-6 border-2 hover:border-primary-300 transition-colors"
        :class="{
          'border-green-300': discount.is_active && !isExpired(discount),
          'border-gray-200': !discount.is_active || isExpired(discount)
        }"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-mono font-bold text-xl text-primary-600">{{ discount.code || discount.discount_code }}</span>
              <button
                @click="copyCode(discount.code || discount.discount_code)"
                class="text-blue-600 hover:text-blue-800 text-sm"
                title="Copy code"
              >
                📋
              </button>
            </div>
            <div v-if="discount.description" class="text-sm text-gray-600 mb-2">
              {{ discount.description }}
            </div>
          </div>
          <span
            :class="discount.discount_type === 'percent' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'"
            class="px-2 py-1 rounded-full text-xs font-medium"
          >
            {{ discount.discount_type === 'percent' ? 'Percentage' : 'Fixed' }}
          </span>
        </div>

        <div class="mb-4">
          <div class="text-2xl font-bold text-gray-900 mb-1">
            <span v-if="discount.discount_type === 'percent'">
              {{ discount.value || discount.discount_value }}% OFF
            </span>
            <span v-else>
              ${{ discount.value || discount.discount_value }} OFF
            </span>
          </div>
          <div v-if="discount.min_order_value" class="text-xs text-gray-500">
            Minimum order: ${{ discount.min_order_value }}
          </div>
        </div>

        <div class="space-y-2 text-xs text-gray-500 mb-4">
          <div v-if="discount.end_date || discount.expiry_date" class="flex items-center gap-1">
            <span>⏰</span>
            <span>Valid until: {{ formatDate(discount.end_date || discount.expiry_date) }}</span>
          </div>
          <div v-if="discount.max_uses || discount.usage_limit" class="flex items-center gap-1">
            <span>📊</span>
            <span>
              {{ discount.used_count || 0 }} / {{ discount.max_uses || discount.usage_limit }} uses
            </span>
          </div>
          <div v-if="discount.applies_to_first_order_only" class="flex items-center gap-1 text-orange-600">
            <span>🎁</span>
            <span>First order only</span>
          </div>
        </div>

        <div class="flex items-center justify-between pt-4 border-t">
          <span
            :class="getStatusClass(discount)"
            class="px-2 py-1 rounded-full text-xs font-medium"
          >
            {{ getStatusText(discount) }}
          </span>
          <button
            @click="copyCode(discount.code || discount.discount_code)"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
          >
            Copy Code
          </button>
        </div>
      </div>
    </div>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import discountsAPI from '@/api/discounts'

const discounts = ref([])
const loading = ref(false)

const filters = ref({
  search: '',
  discount_type: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadDiscounts()
  }, 500)
}

const loadDiscounts = async () => {
  loading.value = true
  try {
    // Use my_discounts endpoint which is accessible to clients
    const res = await discountsAPI.myDiscounts()
    let allDiscounts = res.data.results || res.data || []
    
    // Apply client-side filtering for search and discount type
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      allDiscounts = allDiscounts.filter(d => 
        d.discount_code?.toLowerCase().includes(searchLower) ||
        d.description?.toLowerCase().includes(searchLower)
      )
    }
    
    if (filters.value.discount_type) {
      allDiscounts = allDiscounts.filter(d => d.discount_type === filters.value.discount_type)
    }
    
    // Filter out expired discounts
    allDiscounts = allDiscounts.filter(d => !isExpired(d))
    
    discounts.value = allDiscounts
  } catch (error) {
    // Handle 403 (Forbidden) gracefully - user doesn't have permission
    if (error.response?.status === 403) {
      discounts.value = []
      // Don't show error message for permission issues - just show empty state
      return
    }
    // Only show error for other types of errors
    if (error.response?.status !== 404) {
      showMessage('Failed to load discounts: ' + (error.response?.data?.detail || error.message), false)
    }
    discounts.value = []
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    discount_type: '',
  }
  loadDiscounts()
}

const isExpired = (discount) => {
  if (!discount.end_date && !discount.expiry_date) return false
  const expiry = discount.end_date || discount.expiry_date
  return new Date(expiry) < new Date()
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    showMessage('Discount code copied to clipboard!', true)
  }).catch(() => {
    showMessage('Failed to copy code', false)
  })
}

const getStatusClass = (discount) => {
  if (isExpired(discount)) return 'bg-gray-100 text-gray-800'
  if (!discount.is_active) return 'bg-red-100 text-red-800'
  return 'bg-green-100 text-green-800'
}

const getStatusText = (discount) => {
  if (isExpired(discount)) return 'Expired'
  if (!discount.is_active) return 'Inactive'
  return 'Active'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const message = ref('')
const messageSuccess = ref(false)

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(() => {
  loadDiscounts()
})
</script>

