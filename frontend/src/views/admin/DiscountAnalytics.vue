<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Discount Analytics</h1>
        <p class="mt-2 text-gray-600">Track discount performance, usage, and effectiveness</p>
      </div>
      <button @click="refreshAnalytics" class="btn btn-secondary" :disabled="loading">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Overall Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Discounts</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total_discounts || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Active Discounts</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.active_discounts || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Usage</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.total_usage || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Avg Discount Value</p>
        <p class="text-3xl font-bold text-orange-900">${{ formatCurrency(stats.avg_discount_value) }}</p>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Top Used Discounts -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold mb-4">Top 10 Most Used Discounts</h3>
        <div v-if="topUsedLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="topUsed.length === 0" class="text-center py-12 text-gray-500">
          No discount usage data available
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(discount, index) in topUsed"
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 rounded"
          >
            <div class="flex items-center space-x-3">
              <span class="text-lg font-bold text-gray-400">#{{ index + 1 }}</span>
              <span class="font-medium text-gray-900">{{ discount.code }}</span>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-600">{{ discount.usage_count }} uses</span>
              <div class="w-32 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full"
                  :style="{ width: `${(discount.usage_count / maxUsage) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Events Breakdown -->
      <div class="card p-6">
        <h3 class="text-lg font-semibold mb-4">Discounts by Promotional Campaign</h3>
        <div v-if="eventsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="eventsBreakdown.length === 0" class="text-center py-12 text-gray-500">
          No promotional campaign data available
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(event, index) in eventsBreakdown"
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 rounded"
          >
            <div class="flex items-center space-x-3">
              <span class="font-medium text-gray-900">{{ event.event || 'Unnamed Campaign' }}</span>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-600">{{ event.discount_count }} discounts</span>
              <div class="w-32 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-purple-600 h-2 rounded-full"
                  :style="{ width: `${(event.discount_count / maxEventCount) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Discount Usage Table -->
    <div class="card p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Recent Discount Usage</h3>
        <div class="flex space-x-2">
          <input
            v-model="usageFilters.search"
            @input="debouncedUsageSearch"
            type="text"
            placeholder="Search by discount code..."
            class="border rounded px-3 py-2 text-sm"
          />
        </div>
      </div>
      <div v-if="usageLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Discount Code</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Used By</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Discount Amount</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Used At</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="usage in discountUsage" :key="usage.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ usage.discount_code || usage.discount?.discount_code || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ usage.user_name || usage.user || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#{{ usage.order_id || usage.order || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{ formatCurrency(usage.discount_amount || usage.amount || 0) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDateTime(usage.used_at || usage.created_at) }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="!usageLoading && discountUsage.length === 0" class="text-center py-12 text-gray-500">
        No discount usage found
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { discountsAPI } from '@/api'

const loading = ref(false)
const stats = ref({})
const topUsed = ref([])
const eventsBreakdown = ref([])
const discountUsage = ref([])

const topUsedLoading = ref(false)
const eventsLoading = ref(false)
const usageLoading = ref(false)

const usageFilters = ref({
  search: '',
})

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const maxUsage = computed(() => {
  if (topUsed.value.length === 0) return 1
  return Math.max(...topUsed.value.map(d => d.usage_count))
})

const maxEventCount = computed(() => {
  if (eventsBreakdown.value.length === 0) return 1
  return Math.max(...eventsBreakdown.value.map(e => e.discount_count))
})

const loadOverallStats = async () => {
  try {
    const response = await discountsAPI.getOverallStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load overall stats:', error)
  }
}

const loadTopUsed = async () => {
  topUsedLoading.value = true
  try {
    const response = await discountsAPI.getTopUsed()
    topUsed.value = response.data || []
  } catch (error) {
    console.error('Failed to load top used discounts:', error)
  } finally {
    topUsedLoading.value = false
  }
}

const loadEventsBreakdown = async () => {
  eventsLoading.value = true
  try {
    const response = await discountsAPI.getEventsBreakdown()
    eventsBreakdown.value = response.data || []
  } catch (error) {
    console.error('Failed to load events breakdown:', error)
  } finally {
    eventsLoading.value = false
  }
}

const loadDiscountUsage = async () => {
  usageLoading.value = true
  try {
    const params = {}
    if (usageFilters.value.search) {
      // Note: Backend may need to support search by discount code
      params.search = usageFilters.value.search
    }
    
    const response = await discountsAPI.listUsage(params)
    discountUsage.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load discount usage:', error)
  } finally {
    usageLoading.value = false
  }
}

let usageSearchTimeout = null
const debouncedUsageSearch = () => {
  if (usageSearchTimeout) clearTimeout(usageSearchTimeout)
  usageSearchTimeout = setTimeout(() => {
    loadDiscountUsage()
  }, 500)
}

const refreshAnalytics = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadOverallStats(),
      loadTopUsed(),
      loadEventsBreakdown(),
      loadDiscountUsage(),
    ])
  } catch (error) {
    console.error('Failed to refresh analytics:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshAnalytics()
})
</script>

