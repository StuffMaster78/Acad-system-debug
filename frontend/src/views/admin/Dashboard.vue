<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
      <div>
          <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>Time period:</span>
            <select 
              v-model="timePeriod" 
              @change="loadDashboard"
              class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
              <option value="all">All time</option>
            </select>
      </div>
      <button 
        @click="refreshDashboard" 
        :disabled="loading" 
            class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm font-medium"
      >
        <svg 
              class="w-4 h-4" 
          :class="{ 'animate-spin': loading }"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
            {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>
          </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="flex flex-col items-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
          <p class="text-sm font-medium text-gray-500">Loading dashboard data...</p>
        </div>
        </div>
        
      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <p class="text-sm text-red-800">{{ error }}</p>
          </div>
          <button @click="refreshDashboard" class="text-sm text-red-600 hover:text-red-800 underline">
            Retry
          </button>
        </div>
        </div>
        
      <!-- Dashboard Content -->
      <div v-else class="space-y-6">
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Total Clients -->
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Total customers</span>
              <div class="flex items-center gap-1 text-green-600 text-xs font-medium">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <span>{{ formatPercentageChange(clientsChange) }}</span>
              </div>
            </div>
            <div class="text-3xl font-bold text-gray-900">{{ formatNumber(dashboardData.total_clients || 0) }}</div>
          </div>

          <!-- Total Revenue -->
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Total revenue</span>
              <div class="flex items-center gap-1 text-green-600 text-xs font-medium">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <span>{{ formatPercentageChange(revenueChange) }}</span>
              </div>
            </div>
            <div class="text-3xl font-bold text-gray-900">${{ formatCurrencyShort(dashboardData.total_revenue || 0) }}</div>
          </div>

          <!-- Total Orders -->
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Total orders</span>
              <div class="flex items-center gap-1 text-red-600 text-xs font-medium">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
                <span>{{ formatPercentageChange(ordersChange) }}</span>
          </div>
        </div>
            <div class="text-3xl font-bold text-gray-900">{{ formatNumber(dashboardData.total_orders || 0) }}</div>
          </div>

          <!-- Completed Orders -->
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Completed</span>
              <div class="flex items-center gap-1 text-green-600 text-xs font-medium">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <span>{{ formatPercentageChange(completedChange) }}</span>
              </div>
            </div>
            <div class="text-3xl font-bold text-gray-900">{{ formatNumber(dashboardData.completed_orders || 0) }}</div>
          </div>
        </div>
        
        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Order Trends Chart -->
          <div class="lg:col-span-2 bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-lg font-semibold text-gray-900">Order trends.</h2>
              <div class="flex items-center gap-4 text-xs">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 rounded-full bg-blue-500"></div>
                  <span class="text-gray-600">Orders</span>
                </div>
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 rounded-full bg-green-500"></div>
                  <span class="text-gray-600">Revenue</span>
                </div>
              </div>
            </div>
            <div v-if="orderTrendsLoading" class="flex items-center justify-center h-64">
              <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-200 border-t-blue-600"></div>
            </div>
            <apexchart
              v-else
              type="bar"
              height="300"
              :options="orderTrendsChartOptions"
              :series="orderTrendsSeries"
            />
          </div>

          <!-- Orders by Status -->
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 mb-6">Orders by status.</h2>
            <div v-if="orderStatusLoading" class="flex items-center justify-center h-64">
              <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-200 border-t-blue-600"></div>
            </div>
            <div v-else class="space-y-4">
              <apexchart
                type="donut"
                height="250"
                :options="orderStatusChartOptions"
                :series="orderStatusSeries"
              />
              <div class="space-y-2 mt-4">
                <div 
                  v-for="(item, index) in orderStatusBreakdown" 
                  :key="index"
                  class="flex items-center justify-between text-sm"
                >
                  <div class="flex items-center gap-2">
                    <div 
                      class="w-3 h-3 rounded-full" 
                      :style="{ backgroundColor: statusColors[index % statusColors.length] }"
                    ></div>
                    <span class="text-gray-700">{{ item.label }}</span>
                  </div>
                  <span class="font-semibold text-gray-900">{{ item.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Bottom Section: Service Types & Top Performers -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Orders by Service Type -->
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 mb-6">Orders by service type.</h2>
            <div v-if="serviceTypeLoading" class="flex items-center justify-center h-64">
              <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-200 border-t-blue-600"></div>
            </div>
            <div v-else class="space-y-3">
              <div 
                v-for="(item, index) in serviceTypeBreakdown" 
                :key="index"
                class="flex items-center justify-between"
              >
                <div class="flex items-center gap-3 flex-1 min-w-0">
                  <div 
                    class="w-4 h-4 rounded" 
                    :style="{ backgroundColor: serviceColors[index % serviceColors.length] }"
                  ></div>
                  <span class="text-sm text-gray-700 truncate">{{ item.name }}</span>
                </div>
                <div class="flex items-center gap-4 ml-4">
                  <span class="text-sm font-semibold text-gray-900">{{ item.percentage }}%</span>
                  <span class="text-xs text-gray-500 w-16 text-right">{{ formatNumber(item.count) }}</span>
          </div>
          </div>
        </div>
      </div>

          <!-- Top Clients -->
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900 mb-6">Top clients.</h2>
            <div v-if="topClientsLoading" class="flex items-center justify-center h-64">
              <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-200 border-t-blue-600"></div>
            </div>
            <div v-else-if="topClients.length === 0" class="flex items-center justify-center h-64 text-gray-400">
              <p class="text-sm">No top client data available.</p>
            </div>
            <div v-else class="overflow-x-auto">
              <div class="flex gap-4 pb-2" style="min-width: max-content;">
                <div 
                  v-for="(client, index) in topClients.slice(0, 10)" 
                  :key="index"
                  class="shrink-0 w-48 bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow"
                >
                  <div class="flex items-center gap-2 mb-2">
                    <div class="w-2 h-2 rounded-full bg-green-500"></div>
                    <span class="text-xs font-semibold text-gray-500">#{{ index + 1 }}</span>
                  </div>
                  <div class="mb-2">
                    <p class="text-sm font-semibold text-gray-900 truncate" :title="client.name || client.email || `Client #${client.id}`">
                      {{ client.name || client.email || `Client #${client.id}` }}
                    </p>
                  </div>
                  <div class="flex items-baseline justify-between">
                    <span class="text-xs text-gray-500">Revenue</span>
                    <span class="text-sm font-bold text-green-600">{{ formatCurrency(client.revenue || 0) }}</span>
                  </div>
                  <div class="mt-1 flex items-center justify-between">
                    <span class="text-xs text-gray-500">Share</span>
                    <span class="text-xs font-semibold text-gray-700">{{ client.percentage }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'

    const authStore = useAuthStore()

const loading = ref(false)
const error = ref(null)
const dashboardData = ref({})
const timePeriod = ref('30')
const orderTrendsLoading = ref(false)
const orderStatusLoading = ref(false)
const serviceTypeLoading = ref(false)
const topClientsLoading = ref(false)

// Chart data
const orderTrendsData = ref([])
const orderStatusData = ref({})
const serviceTypeData = ref([])
const topClientsData = ref([])

// Color palettes
const statusColors = [
  '#8B5CF6', '#EC4899', '#3B82F6', '#10B981', '#F59E0B', 
  '#EF4444', '#6366F1', '#14B8A6', '#F97316', '#84CC16'
]

const serviceColors = [
  '#8B5CF6', '#EC4899', '#3B82F6', '#10B981', '#F59E0B', 
  '#EF4444', '#6366F1', '#14B8A6', '#F97316', '#84CC16'
]

// Computed properties for percentage changes (mock data for now - can be replaced with real comparison data)
const clientsChange = computed(() => {
  // Mock: calculate from previous period
  return 2.5
})

const revenueChange = computed(() => {
  return 0.5
})

const ordersChange = computed(() => {
  return -0.2
})

const completedChange = computed(() => {
  const completed = dashboardData.value.completed_orders || 0
  const total = dashboardData.value.total_orders || 1
  const prevCompleted = completed * 0.99 // Mock previous value
  const prevTotal = total * 0.998
  if (prevCompleted === 0) return 0
  const currentRate = (completed / total) * 100
  const prevRate = (prevCompleted / prevTotal) * 100
  return ((currentRate - prevRate) / prevRate) * 100
})

// Chart options and series
const orderTrendsChartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    fontFamily: 'Inter, sans-serif',
  },
  colors: ['#3B82F6', '#10B981'],
  dataLabels: { enabled: false },
  xaxis: {
    categories: orderTrendsData.value.map(item => item.date),
    labels: { style: { fontSize: '12px', colors: '#6B7280' } }
  },
  yaxis: {
    labels: { 
      style: { fontSize: '12px', colors: '#6B7280' },
      formatter: (val) => formatNumber(val)
    }
  },
  legend: { show: false },
  grid: {
    borderColor: '#E5E7EB',
    strokeDashArray: 4,
  },
  plotOptions: {
    bar: {
      borderRadius: 4,
      columnWidth: '60%',
    }
  }
}))

const orderTrendsSeries = computed(() => [
  {
    name: 'Orders',
    data: orderTrendsData.value.map(item => item.orders)
  },
  {
    name: 'Revenue',
    data: orderTrendsData.value.map(item => item.revenue)
  }
])

const orderStatusChartOptions = computed(() => ({
  chart: {
    type: 'donut',
    fontFamily: 'Inter, sans-serif',
  },
  colors: statusColors,
  labels: orderStatusBreakdown.value.map(item => item.label),
  legend: { show: false },
  dataLabels: { enabled: false },
  plotOptions: {
    pie: {
      donut: {
        size: '70%'
      }
    }
  }
}))

const orderStatusSeries = computed(() => 
  orderStatusBreakdown.value.map(item => item.count)
)

const orderStatusBreakdown = computed(() => {
  if (!orderStatusData.value || Object.keys(orderStatusData.value).length === 0) {
    return []
  }
  const total = Object.values(orderStatusData.value).reduce((sum, val) => sum + val, 0)
  if (total === 0) return []
  
  return Object.entries(orderStatusData.value)
    .map(([status, count]) => ({
      label: formatStatus(status),
      count,
      percentage: ((count / total) * 100).toFixed(1)
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8)
})

const serviceTypeBreakdown = computed(() => {
  if (!serviceTypeData.value || serviceTypeData.value.length === 0) {
    return []
  }
  const total = serviceTypeData.value.reduce((sum, item) => sum + (item.count || 0), 0)
  if (total === 0) return []
  
  return serviceTypeData.value
    .map(item => ({
      name: item.name || item.service_type || 'Unknown',
      count: item.count || 0,
      percentage: (((item.count || 0) / total) * 100).toFixed(1)
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
})

const topClients = computed(() => {
  if (!topClientsData.value || topClientsData.value.length === 0) {
    return []
  }
  const totalRevenue = topClientsData.value.reduce((sum, client) => sum + parseFloat(client.revenue || 0), 0)
  if (totalRevenue === 0) return []
  
  return topClientsData.value
    .map(client => ({
      ...client,
      percentage: ((parseFloat(client.revenue || 0) / totalRevenue) * 100).toFixed(1)
    }))
    .sort((a, b) => parseFloat(b.revenue || 0) - parseFloat(a.revenue || 0))
    .slice(0, 8)
})

const loadDashboard = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Load main dashboard data
    const response = await adminManagementAPI.getDashboard({ days: timePeriod.value === 'all' ? null : parseInt(timePeriod.value) })
    dashboardData.value = response.data || {}
    
    // Load analytics data in parallel
    await Promise.all([
      loadOrderTrends(),
      loadOrderStatus(),
      loadServiceTypes(),
      loadTopClients()
    ])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load dashboard'
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
}

const loadOrderTrends = async () => {
  orderTrendsLoading.value = true
  try {
    const days = timePeriod.value === 'all' ? 30 : parseInt(timePeriod.value)
    const response = await adminManagementAPI.getOrderAnalytics({ days })
    
    // Transform weekly trends to daily for better visualization
    if (response.data?.weekly_trends) {
      // Mock daily data from weekly (in real app, use daily endpoint)
      const trends = response.data.weekly_trends.slice(-14) // Last 14 weeks
      orderTrendsData.value = trends.map((item, index) => ({
        date: formatDateShort(item.week),
        orders: item.created || 0,
        revenue: parseFloat(item.revenue || 0)
      }))
    } else {
      // Fallback: generate mock data
      orderTrendsData.value = generateMockTrendData(days)
    }
  } catch (err) {
    console.error('Failed to load order trends:', err)
    orderTrendsData.value = generateMockTrendData(parseInt(timePeriod.value) || 30)
  } finally {
    orderTrendsLoading.value = false
  }
}

const loadOrderStatus = async () => {
  orderStatusLoading.value = true
  try {
    if (dashboardData.value.orders_by_status) {
      orderStatusData.value = dashboardData.value.orders_by_status
    } else {
      // Fallback: use mock data
      orderStatusData.value = {
        completed: dashboardData.value.completed_orders || 0,
        in_progress: dashboardData.value.orders_in_progress || 0,
        pending: dashboardData.value.pending_orders || 0,
        on_revision: dashboardData.value.orders_on_revision || 0,
      }
    }
  } catch (err) {
    console.error('Failed to load order status:', err)
    orderStatusData.value = {}
  } finally {
    orderStatusLoading.value = false
  }
}

const loadServiceTypes = async () => {
  serviceTypeLoading.value = true
  try {
    const response = await adminManagementAPI.getOrderAnalytics({ days: timePeriod.value === 'all' ? 365 : parseInt(timePeriod.value) })
    if (response.data?.service_breakdown) {
      serviceTypeData.value = response.data.service_breakdown
    } else {
      serviceTypeData.value = []
    }
  } catch (err) {
    console.error('Failed to load service types:', err)
    serviceTypeData.value = []
  } finally {
    serviceTypeLoading.value = false
  }
}

const loadTopClients = async () => {
  topClientsLoading.value = true
  try {
    if (dashboardData.value.top_clients) {
      topClientsData.value = dashboardData.value.top_clients
    } else {
      topClientsData.value = []
    }
  } catch (err) {
    console.error('Failed to load top clients:', err)
    topClientsData.value = []
  } finally {
    topClientsLoading.value = false
  }
}

const refreshDashboard = () => {
  loadDashboard()
}

// Utility functions
const formatNumber = (value) => {
  const num = parseInt(value || 0)
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toLocaleString()
}

const formatCurrency = (value) => {
  const num = parseFloat(value || 0)
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatCurrencyShort = (value) => {
  const num = parseFloat(value || 0)
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toFixed(2)
}

const formatPercentageChange = (value) => {
  if (!value) return '0%'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

const formatStatus = (status) => {
  const statusMap = {
    'completed': 'Completed',
    'in_progress': 'In Progress',
    'pending': 'Pending',
    'on_revision': 'On Revision',
    'submitted': 'Submitted',
    'under_editing': 'Under Editing',
    'disputed': 'Disputed',
    'cancelled': 'Cancelled',
  }
  return statusMap[status] || status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDateShort = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const generateMockTrendData = (days) => {
  const data = []
  const today = new Date()
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    data.push({
      date: formatDateShort(date.toISOString()),
      orders: Math.floor(Math.random() * 50) + 20,
      revenue: Math.floor(Math.random() * 50000) + 10000
    })
  }
  return data
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
