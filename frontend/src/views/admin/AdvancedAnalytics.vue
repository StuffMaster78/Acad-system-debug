<template>
  <div class="advanced-analytics space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
        <p class="mt-2 text-gray-600">Comprehensive business intelligence and performance metrics</p>
      </div>
      <div class="flex gap-2">
        <button @click="exportToCSV" class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
          Export CSV
        </button>
        <button @click="refreshAnalytics" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Date Range Filter -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex items-center gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">From Date</label>
          <input
            v-model="dateFrom"
            type="date"
            class="border rounded px-3 py-2"
            @change="loadAnalytics"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">To Date</label>
          <input
            v-model="dateTo"
            type="date"
            class="border rounded px-3 py-2"
            @change="loadAnalytics"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Year</label>
          <select
            v-model.number="selectedYear"
            @change="loadAnalytics"
            class="border rounded px-3 py-2"
          >
            <option :value="null">All Years</option>
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Month</label>
          <select
            v-model.number="selectedMonth"
            @change="loadAnalytics"
            class="border rounded px-3 py-2"
          >
            <option :value="null">All Months</option>
            <option v-for="(month, idx) in months" :key="idx" :value="idx + 1">{{ month }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Key Metrics Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Revenue</p>
            <p class="text-2xl font-bold text-gray-900">${{ formatCurrency(summary.total_revenue || 0) }}</p>
          </div>
          <div class="text-green-500 text-3xl">💰</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Orders</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.total_orders || 0 }}</p>
          </div>
          <div class="text-blue-500 text-3xl">📦</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Paid Orders</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.paid_orders_count || 0 }}</p>
          </div>
          <div class="text-purple-500 text-3xl">✅</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Unpaid Orders</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.unpaid_orders_count || 0 }}</p>
          </div>
          <div class="text-orange-500 text-3xl">⏳</div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Revenue Trend (Yearly) -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Revenue Trend (Yearly)</h3>
        <div v-if="yearlyLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="yearlyData.length === 0" class="text-center py-12 text-gray-500">
          No data available
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="(month, index) in yearlyData"
            :key="index"
            class="flex items-center justify-between p-2 bg-gray-50 rounded"
          >
            <span class="text-sm font-medium">{{ month.month_name }}</span>
            <div class="flex items-center gap-4">
              <span class="text-sm text-gray-600">{{ month.order_count }} orders</span>
              <span class="text-sm font-bold text-green-600">${{ formatCurrency(month.revenue) }}</span>
              <div class="w-32 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-green-600 h-2 rounded-full"
                  :style="{ width: `${(month.revenue / maxRevenue) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Orders (Daily Breakdown) -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Monthly Orders (Daily Breakdown)</h3>
        <div v-if="monthlyLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="monthlyData.length === 0" class="text-center py-12 text-gray-500">
          No data available for selected month
        </div>
        <div v-else class="space-y-2 max-h-96 overflow-y-auto">
          <div
            v-for="(day, index) in monthlyData"
            :key="index"
            class="flex items-center justify-between p-2 bg-gray-50 rounded"
          >
            <span class="text-sm font-medium">Day {{ day.day }}</span>
            <div class="flex items-center gap-4">
              <span class="text-sm text-gray-600">{{ day.order_count }} orders</span>
              <span class="text-sm font-bold text-blue-600">${{ formatCurrency(day.revenue) }}</span>
              <div class="w-24 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full"
                  :style="{ width: `${(day.order_count / maxDailyOrders) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Revenue Breakdown -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Service Revenue Breakdown</h3>
        <select
          v-model.number="serviceRevenueDays"
          @change="loadServiceRevenue"
          class="border rounded px-3 py-2"
        >
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="365">Last year</option>
        </select>
      </div>
      <div v-if="serviceRevenueLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!serviceRevenueData" class="text-center py-12 text-gray-500">
        No service revenue data available
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- By Paper Type -->
        <div>
          <h4 class="font-semibold mb-3">By Paper Type</h4>
          <div v-if="serviceRevenueData.by_paper_type?.length === 0" class="text-sm text-gray-500">
            No paper type data
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="(item, index) in serviceRevenueData.by_paper_type"
              :key="index"
              class="flex items-center justify-between p-3 bg-gray-50 rounded"
            >
              <span class="text-sm font-medium">{{ item.name }}</span>
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-600">{{ item.order_count }} orders</span>
                <span class="text-sm font-bold">${{ formatCurrency(item.revenue) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- By Additional Service -->
        <div>
          <h4 class="font-semibold mb-3">By Additional Service</h4>
          <div v-if="serviceRevenueData.by_service?.length === 0" class="text-sm text-gray-500">
            No additional service data
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="(item, index) in serviceRevenueData.by_service"
              :key="index"
              class="flex items-center justify-between p-3 bg-gray-50 rounded"
            >
              <span class="text-sm font-medium">{{ item.name }}</span>
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-600">{{ item.order_count }} orders</span>
                <span class="text-sm font-bold">${{ formatCurrency(item.revenue) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Status Breakdown -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold mb-4">Payment Status Breakdown</h3>
      <div v-if="paymentStatusLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!paymentStatusData" class="text-center py-12 text-gray-500">
        No payment status data available
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="p-4 bg-green-50 rounded-lg border border-green-200">
          <h4 class="font-semibold text-green-800 mb-2">Paid Orders</h4>
          <p class="text-2xl font-bold text-green-900">{{ paymentStatusData.paid?.count || 0 }}</p>
          <p class="text-sm text-green-700 mt-1">Revenue: ${{ formatCurrency(paymentStatusData.paid?.revenue || 0) }}</p>
        </div>
        <div class="p-4 bg-orange-50 rounded-lg border border-orange-200">
          <h4 class="font-semibold text-orange-800 mb-2">Unpaid Orders</h4>
          <p class="text-2xl font-bold text-orange-900">{{ paymentStatusData.unpaid?.count || 0 }}</p>
          <p class="text-sm text-orange-700 mt-1">Pending revenue</p>
        </div>
      </div>
    </div>

    <!-- Orders by Status -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold mb-4">Orders by Status</h3>
      <div v-if="!summary.orders_by_status || Object.keys(summary.orders_by_status).length === 0" class="text-center py-12 text-gray-500">
        No order status data available
      </div>
      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          v-for="(count, status) in summary.orders_by_status"
          :key="status"
          class="p-4 bg-gray-50 rounded-lg"
        >
          <p class="text-sm text-gray-600 capitalize">{{ status.replace('_', ' ') }}</p>
          <p class="text-2xl font-bold text-gray-900">{{ count }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { advancedAnalyticsAPI } from '@/api'

const loading = ref(false)
const summary = ref({})
const yearlyData = ref([])
const monthlyData = ref([])
const serviceRevenueData = ref(null)
const paymentStatusData = ref(null)

const yearlyLoading = ref(false)
const monthlyLoading = ref(false)
const serviceRevenueLoading = ref(false)
const paymentStatusLoading = ref(false)

const dateFrom = ref('')
const dateTo = ref('')
const selectedYear = ref(new Date().getFullYear())
const selectedMonth = ref(null)
const serviceRevenueDays = ref(30)

const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const availableYears = computed(() => {
  const years = []
  const currentYear = new Date().getFullYear()
  for (let i = currentYear; i >= currentYear - 5; i--) {
    years.push(i)
  }
  return years
})

const maxRevenue = computed(() => {
  if (yearlyData.value.length === 0) return 1
  return Math.max(...yearlyData.value.map(m => m.revenue), 1)
})

const maxDailyOrders = computed(() => {
  if (monthlyData.value.length === 0) return 1
  return Math.max(...monthlyData.value.map(d => d.order_count), 1)
})

const loadSummary = async () => {
  try {
    const response = await advancedAnalyticsAPI.getSummary()
    summary.value = response.data || {}
  } catch (error) {
    console.error('Error loading summary:', error)
    summary.value = {}
  }
}

const loadYearlyData = async () => {
  yearlyLoading.value = true
  try {
    const response = await advancedAnalyticsAPI.getYearlyOrders(selectedYear.value)
    yearlyData.value = response.data || []
  } catch (error) {
    console.error('Error loading yearly data:', error)
    yearlyData.value = []
  } finally {
    yearlyLoading.value = false
  }
}

const loadMonthlyData = async () => {
  if (!selectedYear.value || !selectedMonth.value) {
    monthlyData.value = []
    return
  }
  
  monthlyLoading.value = true
  try {
    const response = await advancedAnalyticsAPI.getMonthlyOrders(selectedYear.value, selectedMonth.value)
    monthlyData.value = response.data || []
  } catch (error) {
    console.error('Error loading monthly data:', error)
    monthlyData.value = []
  } finally {
    monthlyLoading.value = false
  }
}

const loadServiceRevenue = async () => {
  serviceRevenueLoading.value = true
  try {
    const response = await advancedAnalyticsAPI.getServiceRevenue(serviceRevenueDays.value)
    serviceRevenueData.value = response.data || null
  } catch (error) {
    console.error('Error loading service revenue:', error)
    serviceRevenueData.value = null
  } finally {
    serviceRevenueLoading.value = false
  }
}

const loadPaymentStatus = async () => {
  paymentStatusLoading.value = true
  try {
    const response = await advancedAnalyticsAPI.getPaymentStatus()
    paymentStatusData.value = response.data || null
  } catch (error) {
    console.error('Error loading payment status:', error)
    paymentStatusData.value = null
  } finally {
    paymentStatusLoading.value = false
  }
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadSummary(),
      loadYearlyData(),
      loadMonthlyData(),
      loadServiceRevenue(),
      loadPaymentStatus(),
    ])
  } catch (error) {
    console.error('Error loading analytics:', error)
  } finally {
    loading.value = false
  }
}

const refreshAnalytics = () => {
  loadAnalytics()
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const exportToCSV = () => {
  // Simple CSV export
  const csvRows = []
  
  // Summary data
  csvRows.push(['Metric', 'Value'])
  csvRows.push(['Total Revenue', summary.value.total_revenue || 0])
  csvRows.push(['Total Orders', summary.value.total_orders || 0])
  csvRows.push(['Paid Orders', summary.value.paid_orders_count || 0])
  csvRows.push(['Unpaid Orders', summary.value.unpaid_orders_count || 0])
  csvRows.push([])
  
  // Yearly data
  csvRows.push(['Month', 'Orders', 'Revenue'])
  yearlyData.value.forEach(month => {
    csvRows.push([month.month_name, month.order_count, month.revenue])
  })
  csvRows.push([])
  
  // Monthly data
  if (monthlyData.value.length > 0) {
    csvRows.push(['Day', 'Orders', 'Revenue'])
    monthlyData.value.forEach(day => {
      csvRows.push([day.day, day.order_count, day.revenue])
    })
  }
  
  const csvContent = csvRows.map(row => row.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analytics-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  loadAnalytics()
})
</script>

<style scoped>
.advanced-analytics {
  min-height: 100vh;
  background-color: #f9fafb;
}
</style>

