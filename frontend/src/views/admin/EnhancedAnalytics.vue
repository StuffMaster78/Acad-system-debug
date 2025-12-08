<template>
  <div class="enhanced-analytics p-6">
    <PageHeader 
      title="Enhanced Analytics" 
      subtitle="Deep insights and performance trends"
      :show-refresh="true"
      @refresh="loadAnalytics"
    />
    
    <!-- Loading State -->
    <div v-if="loading" class="mt-6">
      <SkeletonLoader type="stats" />
    </div>
    
    <!-- Error State -->
    <ErrorBoundary v-else-if="error" :error-message="error" @retry="loadAnalytics" />
    
    <!-- Analytics Content -->
    <div v-else-if="analyticsData" class="mt-6 space-y-6">
      <!-- Insights Cards -->
      <div v-if="analyticsData.insights && analyticsData.insights.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="(insight, index) in analyticsData.insights"
          :key="index"
          :class="[
            'p-4 rounded-lg border-l-4',
            insight.type === 'positive' 
              ? 'bg-green-50 dark:bg-green-900/20 border-green-400'
              : insight.type === 'warning'
              ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-400'
              : 'bg-blue-50 dark:bg-blue-900/20 border-blue-400'
          ]"
        >
          <h3 class="font-semibold mb-2">{{ insight.title }}</h3>
          <p class="text-sm mb-2">{{ insight.message }}</p>
          <p class="text-xs font-medium">{{ insight.action }}</p>
        </div>
      </div>
      
      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Client Retention</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Retention Rate</span>
              <span class="font-medium">{{ analyticsData.client_metrics?.retention_rate || 0 }}%</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Active Clients</span>
              <span class="font-medium">{{ analyticsData.client_metrics?.total_active_clients || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Avg Orders/Client</span>
              <span class="font-medium">{{ analyticsData.client_metrics?.avg_orders_per_client || 0 }}</span>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Predictions</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Next Week Revenue</span>
              <span class="font-medium">${{ formatCurrency(analyticsData.predictions?.predicted_revenue_next_week || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Confidence</span>
              <span class="font-medium capitalize">{{ analyticsData.predictions?.confidence || 'N/A' }}</span>
            </div>
          </div>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Top Writers</h3>
          <div class="space-y-2">
            <div
              v-for="(writer, index) in analyticsData.writer_performance?.slice(0, 3)"
              :key="index"
              class="flex justify-between text-sm"
            >
              <span class="truncate">{{ writer.writer_username }}</span>
              <span class="font-medium">{{ writer.completed_orders }} orders</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Revenue Trends Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Daily Revenue Trends</h3>
          <div v-if="loading" class="h-64 flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <apexchart
            v-else-if="revenueTrendsSeries.length > 0"
            type="area"
            height="300"
            :options="revenueTrendsOptions"
            :series="revenueTrendsSeries"
          ></apexchart>
          <div v-else class="h-64 flex items-center justify-center text-gray-500">
            No revenue data available
          </div>
        </div>

        <!-- Daily Order Trends -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold mb-4">Daily Order Trends</h3>
          <div v-if="loading" class="h-64 flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <apexchart
            v-else-if="dailyTrendsSeries.length > 0"
            type="line"
            height="300"
            :options="dailyTrendsOptions"
            :series="dailyTrendsSeries"
          ></apexchart>
          <div v-else class="h-64 flex items-center justify-center text-gray-500">
            No order data available
          </div>
        </div>
      </div>

      <!-- Writer Performance Chart -->
      <div v-if="analyticsData?.writer_performance?.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Top Writers Performance</h3>
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <apexchart
          v-else
          type="bar"
          height="350"
          :options="writerPerformanceOptions"
          :series="writerPerformanceSeries"
        ></apexchart>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
import adminManagementAPI from '@/api/admin-management'
import { getErrorMessage } from '@/utils/errorHandler'

const loading = ref(false)
const error = ref(null)
const analyticsData = ref(null)

const loadAnalytics = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await adminManagementAPI.getEnhancedAnalytics(30)
    analyticsData.value = response.data
  } catch (err) {
    error.value = getErrorMessage(err, 'Failed to load analytics')
    console.error('Failed to load analytics:', err)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num)
}

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return new Intl.NumberFormat('en-US').format(Math.round(num))
}

// Chart Series
const revenueTrendsSeries = computed(() => {
  if (!analyticsData.value?.revenue_trends?.length) return []
  
  return [{
    name: 'Revenue',
    data: analyticsData.value.revenue_trends.map(item => parseFloat(item.revenue || 0))
  }]
})

const dailyTrendsSeries = computed(() => {
  if (!analyticsData.value?.daily_trends?.length) return []
  
  return [
    {
      name: 'Total Orders',
      data: analyticsData.value.daily_trends.map(item => item.total_orders || 0)
    },
    {
      name: 'Completed Orders',
      data: analyticsData.value.daily_trends.map(item => item.completed_orders || 0)
    }
  ]
})

const writerPerformanceSeries = computed(() => {
  if (!analyticsData.value?.writer_performance?.length) return []
  
  const topWriters = analyticsData.value.writer_performance.slice(0, 10)
  
  return [
    {
      name: 'Completed Orders',
      data: topWriters.map(writer => writer.completed_orders || 0)
    },
    {
      name: 'Earnings ($)',
      data: topWriters.map(writer => parseFloat(writer.total_earnings || 0))
    }
  ]
})

// Chart Options
const revenueTrendsOptions = computed(() => ({
  chart: {
    type: 'area',
    toolbar: { show: true },
    zoom: { enabled: true }
  },
  xaxis: {
    categories: analyticsData.value?.revenue_trends?.map(item => {
      if (item.date) {
        return new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return ''
    }).filter(Boolean) || [],
    title: { text: 'Date' }
  },
  yaxis: {
    title: { text: 'Revenue ($)' },
    labels: {
      formatter: (value) => `$${formatNumber(value)}`
    }
  },
  stroke: {
    curve: 'smooth',
    width: 2
  },
  colors: ['#10b981'],
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.3
    }
  },
  tooltip: {
    y: {
      formatter: (value) => `$${formatNumber(value)}`
    }
  },
  dataLabels: {
    enabled: false
  }
}))

const dailyTrendsOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: true },
    zoom: { enabled: true }
  },
  xaxis: {
    categories: analyticsData.value?.daily_trends?.map(item => {
      if (item.date) {
        return new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return ''
    }).filter(Boolean) || [],
    title: { text: 'Date' }
  },
  yaxis: {
    title: { text: 'Number of Orders' }
  },
  stroke: {
    curve: 'smooth',
    width: 2
  },
  colors: ['#3b82f6', '#10b981'],
  markers: {
    size: 4
  },
  legend: {
    position: 'top'
  },
  tooltip: {
    shared: true,
    intersect: false
  }
}))

const writerPerformanceOptions = computed(() => {
  const topWriters = analyticsData.value?.writer_performance?.slice(0, 10) || []
  
  return {
    chart: {
      type: 'bar',
      toolbar: { show: true }
    },
    xaxis: {
      categories: topWriters.map(writer => writer.writer_username || 'Unknown'),
      title: { text: 'Writer' },
      labels: {
        rotate: -45,
        style: {
          fontSize: '12px'
        }
      }
    },
    yaxis: [
      {
        title: { text: 'Orders' },
        opposite: false
      },
      {
        title: { text: 'Earnings ($)' },
        opposite: true,
        labels: {
          formatter: (value) => `$${formatNumber(value)}`
        }
      }
    ],
    colors: ['#3b82f6', '#10b981'],
    legend: {
      position: 'top'
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '55%',
        dataLabels: {
          position: 'top'
        }
      }
    },
    dataLabels: {
      enabled: true,
      formatter: (val) => formatNumber(val)
    },
    tooltip: {
      shared: true,
      intersect: false
    }
  }
})

onMounted(() => {
  loadAnalytics()
})
</script>

