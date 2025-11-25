<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Pricing Analytics Dashboard</h1>
        <p class="mt-2 text-gray-600">Analyze pricing trends, service performance, and optimization opportunities</p>
      </div>
      <div class="flex gap-4">
        <select v-model="dateRange" @change="refreshData" class="border rounded px-3 py-2">
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="365">Last year</option>
        </select>
        <button @click="refreshData" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
        <p class="text-sm text-blue-700 mb-1">Total Revenue</p>
        <p class="text-3xl font-bold text-blue-900">${{ formatCurrency(overview.total_revenue || 0) }}</p>
      </div>
      <div class="bg-green-50 rounded-lg p-6 border border-green-200">
        <p class="text-sm text-green-700 mb-1">Avg Order Value</p>
        <p class="text-3xl font-bold text-green-900">${{ formatCurrency(overview.avg_order_value || 0) }}</p>
      </div>
      <div class="bg-purple-50 rounded-lg p-6 border border-purple-200">
        <p class="text-sm text-purple-700 mb-1">Total Orders</p>
        <p class="text-3xl font-bold text-purple-900">{{ overview.total_orders || 0 }}</p>
      </div>
      <div class="bg-orange-50 rounded-lg p-6 border border-orange-200">
        <p class="text-sm text-orange-700 mb-1">Conversion Rate</p>
        <p class="text-3xl font-bold text-orange-900">{{ (overview.conversion_rate || 0).toFixed(1) }}%</p>
      </div>
    </div>

    <!-- Additional Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-600 mb-1">Avg Base Price</p>
        <p class="text-2xl font-bold text-gray-900">${{ formatCurrency(overview.avg_base_price || 0) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-600 mb-1">Avg Final Total</p>
        <p class="text-2xl font-bold text-gray-900">${{ formatCurrency(overview.avg_final_total || 0) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-600 mb-1">Completed Orders</p>
        <p class="text-2xl font-bold text-gray-900">{{ overview.completed_orders || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Pricing Trends Tab -->
        <div v-if="activeTab === 'trends'" class="space-y-6">
          <h2 class="text-xl font-semibold">Pricing Trends Over Time</h2>
          <div v-if="trendsLoading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else-if="trends.length === 0" class="text-center py-8 text-gray-500">
            No trend data available
          </div>
          <div v-else class="space-y-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <h3 class="text-lg font-semibold mb-4">Revenue & Order Trends</h3>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-100">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Date</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Revenue</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Orders</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Avg Order Value</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="trend in trends.slice(0, 20)" :key="trend.date">
                      <td class="px-4 py-3 text-sm">{{ formatDate(trend.date) }}</td>
                      <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(trend.revenue) }}</td>
                      <td class="px-4 py-3 text-sm">{{ trend.order_count }}</td>
                      <td class="px-4 py-3 text-sm">${{ formatCurrency(trend.avg_order_value) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Service Breakdown Tab -->
        <div v-if="activeTab === 'services'" class="space-y-6">
          <h2 class="text-xl font-semibold">Service Type Breakdown</h2>
          <div v-if="serviceBreakdownLoading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else-if="serviceBreakdown.length === 0" class="text-center py-8 text-gray-500">
            No service data available
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service Type</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order Count</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Revenue</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Revenue</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="service in serviceBreakdown" :key="service.service_type">
                  <td class="px-4 py-3 text-sm font-medium capitalize">{{ service.service_type }}</td>
                  <td class="px-4 py-3 text-sm">{{ service.order_count }}</td>
                  <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(service.total_revenue) }}</td>
                  <td class="px-4 py-3 text-sm">${{ formatCurrency(service.avg_revenue) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Academic Level Breakdown Tab -->
        <div v-if="activeTab === 'academic'" class="space-y-6">
          <h2 class="text-xl font-semibold">Academic Level Breakdown</h2>
          <div v-if="academicBreakdownLoading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else-if="academicBreakdown.length === 0" class="text-center py-8 text-gray-500">
            No academic level data available
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Academic Level</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order Count</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Revenue</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Revenue</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="level in academicBreakdown" :key="level.academic_level">
                  <td class="px-4 py-3 text-sm font-medium">{{ level.academic_level }}</td>
                  <td class="px-4 py-3 text-sm">{{ level.order_count }}</td>
                  <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(level.total_revenue) }}</td>
                  <td class="px-4 py-3 text-sm">${{ formatCurrency(level.avg_revenue) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Pricing Configs Tab -->
        <div v-if="activeTab === 'configs'" class="space-y-6">
          <h2 class="text-xl font-semibold">Pricing Configurations</h2>
          <div v-if="configsLoading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else-if="pricingConfigs.length === 0" class="text-center py-8 text-gray-500">
            No pricing configurations found
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Base Price/Page</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="config in pricingConfigs" :key="config.id">
                  <td class="px-4 py-3 text-sm">{{ config.website }}</td>
                  <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(config.base_price_per_page) }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(config.updated_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Additional Services Tab -->
        <div v-if="activeTab === 'additional'" class="space-y-6">
          <h2 class="text-xl font-semibold">Additional Services Usage</h2>
          <div v-if="additionalServicesLoading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else-if="additionalServices.length === 0" class="text-center py-8 text-gray-500">
            No additional services found
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service Name</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usage Count</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Revenue</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="service in additionalServices" :key="service.id">
                  <td class="px-4 py-3 text-sm font-medium">{{ service.name }}</td>
                  <td class="px-4 py-3 text-sm">${{ formatCurrency(service.price) }}</td>
                  <td class="px-4 py-3 text-sm">{{ service.usage_count }}</td>
                  <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(service.price * service.usage_count) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { pricingAnalyticsAPI } from '@/api'

const activeTab = ref('trends')
const tabs = [
  { id: 'trends', label: 'Pricing Trends' },
  { id: 'services', label: 'Service Breakdown' },
  { id: 'academic', label: 'Academic Level' },
  { id: 'configs', label: 'Pricing Configs' },
  { id: 'additional', label: 'Additional Services' },
]

const loading = ref(false)
const dateRange = ref(30)
const overview = ref({})
const trends = ref([])
const trendsLoading = ref(false)
const serviceBreakdown = ref([])
const serviceBreakdownLoading = ref(false)
const academicBreakdown = ref([])
const academicBreakdownLoading = ref(false)
const pricingConfigs = ref([])
const configsLoading = ref(false)
const additionalServices = ref([])
const additionalServicesLoading = ref(false)

const loadOverview = async () => {
  loading.value = true
  try {
    const response = await pricingAnalyticsAPI.getOverview(dateRange.value)
    overview.value = response.data || {}
  } catch (error) {
    console.error('Error loading overview:', error)
    overview.value = {}
  } finally {
    loading.value = false
  }
}

const loadTrends = async () => {
  trendsLoading.value = true
  try {
    const response = await pricingAnalyticsAPI.getTrends(dateRange.value)
    trends.value = response.data || []
  } catch (error) {
    console.error('Error loading trends:', error)
    trends.value = []
  } finally {
    trendsLoading.value = false
  }
}

const loadServiceBreakdown = async () => {
  serviceBreakdownLoading.value = true
  try {
    const response = await pricingAnalyticsAPI.getServiceBreakdown(dateRange.value)
    serviceBreakdown.value = response.data || []
  } catch (error) {
    console.error('Error loading service breakdown:', error)
    serviceBreakdown.value = []
  } finally {
    serviceBreakdownLoading.value = false
  }
}

const loadAcademicBreakdown = async () => {
  academicBreakdownLoading.value = true
  try {
    const response = await pricingAnalyticsAPI.getAcademicLevelBreakdown(dateRange.value)
    academicBreakdown.value = response.data || []
  } catch (error) {
    console.error('Error loading academic breakdown:', error)
    academicBreakdown.value = []
  } finally {
    academicBreakdownLoading.value = false
  }
}

const loadPricingConfigs = async () => {
  configsLoading.value = true
  try {
    const response = await pricingAnalyticsAPI.getPricingConfigs()
    pricingConfigs.value = response.data || []
  } catch (error) {
    console.error('Error loading pricing configs:', error)
    pricingConfigs.value = []
  } finally {
    configsLoading.value = false
  }
}

const loadAdditionalServices = async () => {
  additionalServicesLoading.value = true
  try {
    const response = await pricingAnalyticsAPI.getAdditionalServices(dateRange.value)
    additionalServices.value = response.data || []
  } catch (error) {
    console.error('Error loading additional services:', error)
    additionalServices.value = []
  } finally {
    additionalServicesLoading.value = false
  }
}

const refreshData = () => {
  loadOverview()
  if (activeTab.value === 'trends') {
    loadTrends()
  } else if (activeTab.value === 'services') {
    loadServiceBreakdown()
  } else if (activeTab.value === 'academic') {
    loadAcademicBreakdown()
  } else if (activeTab.value === 'configs') {
    loadPricingConfigs()
  } else if (activeTab.value === 'additional') {
    loadAdditionalServices()
  }
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

watch(activeTab, (newTab) => {
  if (newTab === 'trends') {
    loadTrends()
  } else if (newTab === 'services') {
    loadServiceBreakdown()
  } else if (newTab === 'academic') {
    loadAcademicBreakdown()
  } else if (newTab === 'configs') {
    loadPricingConfigs()
  } else if (newTab === 'additional') {
    loadAdditionalServices()
  }
})

watch(dateRange, () => {
  refreshData()
})

onMounted(() => {
  loadOverview()
  loadTrends()
})
</script>

<style scoped>
/* Add any custom styles here */
</style>

