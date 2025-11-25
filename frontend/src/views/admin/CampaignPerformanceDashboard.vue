<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Campaign Performance</h1>
        <p class="mt-2 text-gray-600">{{ campaign?.campaign_name || 'Loading campaign details...' }}</p>
      </div>
      <div class="flex gap-2">
        <router-link
          :to="`/admin/campaigns`"
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
        >
          ← Back to Campaigns
        </router-link>
        <button @click="refreshAnalytics" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="loading && !analytics" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="analytics" class="space-y-6">
      <!-- Campaign Info -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span class="text-sm font-medium text-gray-600">Status</span>
            <p class="text-lg font-semibold">
              <span :class="getStatusClass(analytics.status)" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ analytics.status }}
              </span>
            </p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Start Date</span>
            <p class="text-lg font-semibold">{{ formatDateTime(analytics.start_date) }}</p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">End Date</span>
            <p class="text-lg font-semibold">{{ formatDateTime(analytics.end_date) }}</p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Active</span>
            <p class="text-lg font-semibold">{{ analytics.is_active ? 'Yes' : 'No' }}</p>
          </div>
        </div>
      </div>

      <!-- Revenue Metrics -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
          <p class="text-sm font-medium text-green-700 mb-1">Total Revenue</p>
          <p class="text-3xl font-bold text-green-900">${{ formatCurrency(analytics.revenue?.total_revenue || 0) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
          <p class="text-sm font-medium text-blue-700 mb-1">Net Revenue</p>
          <p class="text-3xl font-bold text-blue-900">${{ formatCurrency(analytics.revenue?.net_revenue || 0) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
          <p class="text-sm font-medium text-orange-700 mb-1">Discount Amount</p>
          <p class="text-3xl font-bold text-orange-900">${{ formatCurrency(analytics.revenue?.total_discount_amount || 0) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
          <p class="text-sm font-medium text-purple-700 mb-1">ROI</p>
          <p class="text-3xl font-bold text-purple-900">{{ formatCurrency(analytics.revenue?.roi || 0) }}%</p>
        </div>
      </div>

      <!-- Usage Metrics -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
          <p class="text-sm font-medium text-indigo-700 mb-1">Total Uses</p>
          <p class="text-3xl font-bold text-indigo-900">{{ analytics.usage?.total_uses || 0 }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-teal-50 to-teal-100 border border-teal-200">
          <p class="text-sm font-medium text-teal-700 mb-1">Unique Users</p>
          <p class="text-3xl font-bold text-teal-900">{{ analytics.usage?.unique_users || 0 }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-pink-50 to-pink-100 border border-pink-200">
          <p class="text-sm font-medium text-pink-700 mb-1">Avg Uses/User</p>
          <p class="text-3xl font-bold text-pink-900">{{ formatCurrency(analytics.usage?.avg_uses_per_user || 0) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-cyan-50 to-cyan-100 border border-cyan-200">
          <p class="text-sm font-medium text-cyan-700 mb-1">Avg Order Value</p>
          <p class="text-3xl font-bold text-cyan-900">${{ formatCurrency(analytics.revenue?.avg_order_value || 0) }}</p>
        </div>
      </div>

      <!-- Discounts Overview -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold mb-4">Discounts Overview</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="text-sm font-medium text-gray-600">Total Discounts</span>
            <p class="text-2xl font-bold">{{ analytics.discounts?.total || 0 }}</p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Active Discounts</span>
            <p class="text-2xl font-bold">{{ analytics.discounts?.active || 0 }}</p>
          </div>
        </div>
      </div>

      <!-- Top Discounts -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold mb-4">Top Performing Discounts</h3>
        <div v-if="analytics.top_discounts && analytics.top_discounts.length > 0" class="space-y-3">
          <div
            v-for="(discount, index) in analytics.top_discounts"
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 rounded"
          >
            <div class="flex items-center space-x-3">
              <span class="text-lg font-bold text-gray-400">#{{ index + 1 }}</span>
              <span class="font-medium text-gray-900 font-mono">{{ discount.discount__discount_code }}</span>
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
        <div v-else class="text-center py-12 text-gray-500">
          No discount usage data available
        </div>
      </div>
    </div>

    <div v-else class="bg-white rounded-lg shadow-sm p-12 text-center">
      <p class="text-gray-500 text-lg">Failed to load campaign analytics</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/api/client'

const route = useRoute()
const campaignId = route.params.id

const loading = ref(false)
const analytics = ref(null)
const campaign = ref(null)

const loadAnalytics = async () => {
  loading.value = true
  try {
    const response = await apiClient.get(`/discounts/discounts/analytics/campaign-analytics/${campaignId}/`)
    analytics.value = response.data
    campaign.value = {
      campaign_name: response.data.campaign_name,
      id: response.data.campaign_id
    }
  } catch (error) {
    console.error('Failed to load campaign analytics:', error)
  } finally {
    loading.value = false
  }
}

const refreshAnalytics = () => {
  loadAnalytics()
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const getStatusClass = (status) => {
  const statusMap = {
    draft: 'bg-gray-100 text-gray-800',
    active: 'bg-green-100 text-green-800',
    paused: 'bg-yellow-100 text-yellow-800',
    pending: 'bg-blue-100 text-blue-800',
    completed: 'bg-purple-100 text-purple-800',
    archived: 'bg-gray-100 text-gray-800',
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

const maxUsage = computed(() => {
  if (!analytics.value?.top_discounts || analytics.value.top_discounts.length === 0) return 1
  return Math.max(...analytics.value.top_discounts.map(d => d.usage_count))
})

onMounted(() => {
  loadAnalytics()
})
</script>

